"""Module provides generic interface to running Galaxy tools and workflows."""

import json
import os
import tempfile

import yaml

from bioblend.galaxy.client import Client
from galaxy.tools.parser import get_tool_source
from galaxy.tools.cwl.util import (
    FileUploadTarget,
    galactic_job_json,
    invocation_to_output,
    output_properties,
    output_to_cwl_json,
    tool_response_to_output,
)


from planemo.io import wait_on
from planemo.runnable import (
    ErrorRunResponse,
    get_outputs,
    RunnableType,
    SuccessfulRunResponse,
)

DEFAULT_HISTORY_NAME = "CWL Target History"
ERR_NO_SUCH_TOOL = ("Failed to find tool with ID [%s] in Galaxy - cannot execute job. "
                    "You may need to enable verbose logging and determine why the tool did not load. [%s]")


def execute(ctx, config, runnable, job_path, **kwds):
    """Execute a Galaxy activity."""
    try:
        return _execute(ctx, config, runnable, job_path, **kwds)
    except Exception as e:
        return ErrorRunResponse(str(e))


def _execute(ctx, config, runnable, job_path, **kwds):
    user_gi = config.user_gi
    admin_gi = config.gi

    history_id = _history_id(user_gi, **kwds)

    galaxy_paths, job_dict, datasets = stage_in(config, user_gi, history_id, job_path, **kwds)

    if runnable.type in [RunnableType.galaxy_tool, RunnableType.cwl_tool]:
        response_class = GalaxyToolRunResponse
        tool_id = _tool_id(runnable.path)
        if runnable.type == RunnableType.cwl_tool:
            inputs_representation = "cwl"
        else:
            inputs_representation = "galaxy"
        try:
            user_gi.tools.show_tool(tool_id)
        except Exception as e:
            raise Exception(ERR_NO_SUCH_TOOL % (tool_id, e))
        run_tool_payload = dict(
            history_id=history_id,
            tool_id=tool_id,
            inputs=job_dict,
            inputs_representation=inputs_representation,
        )
        ctx.vlog("Post to Galaxy tool API with payload [%s]" % run_tool_payload)
        tool_run_response = user_gi.tools._tool_post(run_tool_payload)

        job = tool_run_response["jobs"][0]
        job_id = job["id"]
        final_state = _wait_for_job(user_gi, job_id)
        if final_state != "ok":
            msg = "Failed to run CWL tool job final job state is [%s]." % final_state
            with open("errored_galaxy.log", "w") as f:
                f.write(config.log_contents)
            raise Exception(msg)

        ctx.vlog("Final job state was ok, fetching details for job [%s]" % job_id)
        job_info = admin_gi.jobs.show_job(job_id)
        response_kwds = {
            'job_info': job_info,
            'api_run_response': tool_run_response,
        }

    elif runnable.type in [RunnableType.galaxy_workflow, RunnableType.cwl_workflow]:
        response_class = GalaxyWorkflowRunResponse
        workflow_id = config.workflow_id(runnable.path)
        ctx.vlog("Found Galaxy workflow ID [%s] for path [%s]" % (workflow_id, runnable.path))
        # TODO: update bioblend to allow inputs_by.
        # invocation = user_gi.worklfows.invoke_workflow(
        #    workflow_id,
        #    history_id=history_id,
        #    inputs=job_dict,
        # )
        payload = dict(
            workflow_id=workflow_id,
            history_id=history_id,
            inputs=job_dict,
            inputs_by="name",
            allow_tool_state_corrections=True,
        )
        invocations_url = "%s/%s/invocations" % (
            user_gi._make_url(user_gi.workflows),
            workflow_id,
        )
        invocation = Client._post(user_gi.workflows, payload, url=invocations_url)
        invocation_id = invocation["id"]
        ctx.vlog("Waiting for invocation [%s]" % invocation_id)
        final_invocation_state = _wait_for_invocation(user_gi, workflow_id, invocation_id)
        ctx.vlog("Final invocation state is [%s]" % final_invocation_state)
        final_state = _wait_for_history(user_gi, history_id)
        if final_state != "ok":
            msg = "Failed to run workflow final history state is [%s]." % final_state
            with open("errored_galaxy.log", "w") as f:
                f.write(config.log_contents)
            raise Exception(msg)
        ctx.vlog("Final history state is 'ok'")
        response_kwds = {
            'workflow_id': workflow_id,
            'invocation_id': invocation_id,
        }
    else:
        raise NotImplementedError()

    run_response = response_class(
        ctx=ctx,
        runnable=runnable,
        user_gi=user_gi,
        history_id=history_id,
        galaxy_paths=galaxy_paths,
        log=config.log_contents,
        **response_kwds
    )
    output_directory = kwds.get("output_directory", None)
    run_response.collect_outputs(ctx, output_directory)
    return run_response


def stage_in(config, user_gi, history_id, job_path, **kwds):

    def upload_func(upload_target):
        if isinstance(upload_target, FileUploadTarget):
            file_path = upload_target.path
            return user_gi.tools.upload_file(
                file_path,
                history_id,
                file_type="auto",
            )
        else:
            content = json.dumps(upload_target.object)
            return user_gi.tools.paste_content(
                content,
                history_id,
                file_type="expression.json",
            )

    def create_collection_func(element_identifiers, collection_type):
        payload = {
            "name": "dataset collection",
            "instance_type": "history",
            "history_id": history_id,
            "element_identifiers": json.dumps(element_identifiers),
            "collection_type": collection_type,
            "fields": None if collection_type != "record" else "auto",
        }
        dataset_collections_url = user_gi._make_url(user_gi.dataset_collections)
        dataset_collection = Client._post(user_gi.workflows, payload, url=dataset_collections_url)
        return dataset_collection

    with open(job_path, "r") as f:
        job = yaml.load(f)

    # Figure out what "." should be here instead.
    job_dir = os.path.dirname(job_path)
    job_dict, datasets = galactic_job_json(
        job, job_dir, upload_func, create_collection_func
    )

    if datasets:
        final_state = _wait_for_history(user_gi, history_id)
    else:
        # Mark uploads as ok because nothing to do.
        final_state = "ok"

    if final_state != "ok":
        msg = "Failed to run CWL job final job state is [%s]." % final_state
        with open("errored_galaxy.log", "w") as f:
            f.write(config.log_contents)
        raise Exception(msg)

    galaxy_paths = []
    for (dataset, local_path) in datasets:
        dataset_full = user_gi.datasets.show_dataset(dataset["id"])
        galaxy_path = dataset_full["file_name"]
        job_path = os.path.join(job_dir, local_path)
        galaxy_paths.append((job_path, galaxy_path))

    return galaxy_paths, job_dict, datasets


class GalaxyBaseRunResponse(SuccessfulRunResponse):

    def __init__(
        self,
        ctx,
        runnable,
        user_gi,
        history_id,
        galaxy_paths,
        log,
    ):
        self._ctx = ctx
        self._runnable = runnable
        self._user_gi = user_gi
        self._history_id = history_id
        self._log = log

        self._job_info = None

        self.galaxy_paths = galaxy_paths

        self._outputs_dict = None

    def to_galaxy_output(self, output):
        """Convert runnable output to a GalaxyOutput object.

        Subclasses for workflow and tool execution override this.
        """
        raise NotImplementedError()

    def collect_outputs(self, ctx, output_directory):
        assert self._outputs_dict is None, "collect_outputs pre-condition violated"

        outputs_dict = {}
        if not output_directory:
            # TODO: rather than creating a directory just use
            # Galaxy paths if they are available in this
            # configuration.
            output_directory = tempfile.mkdtemp()

        def get_metadata(history_content_type, content_id):
            if history_content_type == "dataset":
                return self._user_gi.histories.show_dataset(
                    self._history_id,
                    content_id,
                )
            elif history_content_type == "dataset_collection":
                return self._user_gi.histories.show_dataset_collection(
                    self._history_id,
                    content_id,
                )
            else:
                raise Exception("Unknown history content type encountered [%s]" % history_content_type)

        def get_dataset(dataset_details):
            destination = self.download_output_to(dataset_details, output_directory)
            return {"path": destination}

        ctx.vlog("collecting outputs to directory %s" % output_directory)
        for runnable_output in get_outputs(self._runnable):
            output_id = runnable_output.get_id()

            output_dict_value = None
            if self._runnable in ["cwl_workflow", "cwl_tool"]:
                galaxy_output = self.to_galaxy_output(runnable_output)

                cwl_output = output_to_cwl_json(
                    galaxy_output,
                    get_metadata,
                    get_dataset,
                )

                output_dict_value = cwl_output
            else:
                output_dataset_id = self.output_dataset_id(runnable_output)
                dataset = get_metadata("dataset", output_dataset_id)
                dataset_dict = get_dataset(dataset)
                ctx.vlog("populated destination [%s]" % dataset_dict["path"])

                if dataset["file_ext"] == "expression.json":
                    with open(dataset_dict["path"], "r") as f:
                        output_dict_value = json.load(f)
                else:
                    output_dict_value = output_properties(**dataset_dict)

            outputs_dict[output_id] = output_dict_value

        ctx.vlog("collected outputs [%s]" % self._outputs_dict)
        self._outputs_dict = outputs_dict

    @property
    def log(self):
        return self._log

    @property
    def job_info(self):
        if self._job_info is not None:
            return dict(
                stdout=self._job_info["stdout"],
                stderr=self._job_info["stderr"],
                command_line=self._job_info["command_line"],
            )
        return None

    @property
    def outputs_dict(self):
        return self._outputs_dict

    def download_output_to(self, dataset_details, output_directory):
        file_name = dataset_details.get("cwl_file_name") or dataset_details.get("name")
        destination = os.path.join(output_directory, file_name)
        self._user_gi.histories.download_dataset(
            self._history_id,
            dataset_details["id"],
            file_path=destination,
            use_default_filename=False,
        )
        return destination


class GalaxyToolRunResponse(GalaxyBaseRunResponse):

    def __init__(
        self,
        ctx,
        runnable,
        user_gi,
        history_id,
        galaxy_paths,
        log,
        job_info,
        api_run_response,
    ):
        super(GalaxyToolRunResponse, self).__init__(
            ctx=ctx,
            runnable=runnable,
            user_gi=user_gi,
            history_id=history_id,
            galaxy_paths=galaxy_paths,
            log=log,
        )
        self._job_info = job_info
        self.api_run_response = api_run_response

    def is_collection(self, output):
        # TODO: Make this more rigorous - search both output and output
        # collections - throw an exception if not found in either place instead
        # of just assuming all non-datasets are collections.
        return self.output_dataset_id(output) is None

    def to_galaxy_output(self, runnable_output):
        output_id = runnable_output.get_id()
        return tool_response_to_output(self.api_run_response, self._history_id, output_id)

    def output_dataset_id(self, output):
        outputs = self.api_run_response["outputs"]
        output_id = output.get_id()
        output_dataset_id = None
        self._ctx.vlog("Looking for id [%s] in outputs [%s]" % (output_id, outputs))
        for output in outputs:
            if output["output_name"] == output_id:
                output_dataset_id = output["id"]

        return output_dataset_id


class GalaxyWorkflowRunResponse(GalaxyBaseRunResponse):

    def __init__(
        self,
        ctx,
        runnable,
        user_gi,
        history_id,
        galaxy_paths,
        log,
        workflow_id,
        invocation_id,
    ):
        super(GalaxyWorkflowRunResponse, self).__init__(
            ctx=ctx,
            runnable=runnable,
            user_gi=user_gi,
            history_id=history_id,
            galaxy_paths=galaxy_paths,
            log=log,
        )
        self._workflow_id = workflow_id
        self._invocation_id = invocation_id

    def to_galaxy_output(self, runnable_output):
        output_id = runnable_output.get_id()
        return invocation_to_output(self._invocation, self._history_id, output_id)

    def output_dataset_id(self, output):
        invocation = self._invocation
        if "outputs" in invocation:
            # Use newer workflow outputs API.

            if output.get_id() in invocation["outputs"]:
                return invocation["outputs"][output.get_id()]["id"]
            else:
                raise Exception("Failed to find output [%s] in invocation outputs [%s]" % invocation["outputs"])
        else:
            # Assume the output knows its order_index and such - older line of
            # development not worth persuing.
            workflow_output = output.workflow_output
            order_index = workflow_output.order_index

            invocation_steps = invocation["steps"]
            output_steps = [s for s in invocation_steps if s["order_index"] == order_index]
            assert len(output_steps) == 1, "More than one step matching outputs, behavior undefined."
            output_step = output_steps[0]
            job_id = output_step["job_id"]
            assert job_id, "Output doesn't define a job_id, behavior undefined."
            job_info = self._user_gi.jobs.show_job(job_id, full_details=True)
            job_outputs = job_info["outputs"]
            output_name = workflow_output.output_name
            assert output_name in job_outputs, "No output [%s] found for output job."
            job_output = job_outputs[output_name]
            assert "id" in job_output, "Job output [%s] does not contain 'id'." % job_output
            return job_output["id"]

    @property
    def _invocation(self):
        invocation = self._user_gi.workflows.show_invocation(
            self._workflow_id,
            self._invocation_id,
        )
        return invocation


def _tool_id(tool_path):
    tool_source = get_tool_source(tool_path)
    return tool_source.parse_id()


def _history_id(gi, **kwds):
    history_id = kwds.get("history_id", None)
    if history_id is None:
        history_name = kwds.get("history_name", DEFAULT_HISTORY_NAME)
        history_id = gi.histories.create_history(history_name)["id"]
    return history_id


def _wait_for_invocation(gi, workflow_id, invocation_id):
    def state_func():
        return gi.workflows.show_invocation(workflow_id, invocation_id)

    return _wait_on_state(state_func)


def _wait_for_history(gi, history_id):
    def state_func():
        return gi.histories.show_history(history_id)

    return _wait_on_state(state_func)


def _wait_for_job(gi, job_id):
    def state_func():
        return gi.jobs.show_job(job_id, full_details=True)

    return _wait_on_state(state_func)


def _wait_on_state(state_func):

    def get_state():
        response = state_func()
        state = response["state"]
        if str(state) not in ["running", "queued", "new", "ready"]:
            return state
        else:
            return None

    final_state = wait_on(get_state, "state", timeout=100)
    return final_state


__all__ = (
    "execute",
)
