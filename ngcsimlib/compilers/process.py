from ngcsimlib.compilers.utils import compose
from ngcsimlib.compilers.process_compiler.component_compiler import compile as compile_component
from ngcsimlib.logger import warn
from functools import wraps
from ngcsimlib.utils import add_component_transition, add_transition_meta
from ngcsimlib.utils import get_current_context, infer_context, Set_Compartment_Batch

class Process(object):
    """
    The process is an alternate method for compiling transitions of models into
    pure methods. In general this is the preferred method for doing this over
    the legacy compiler, however it is not required. The Process composes the
    methods used as they are added to the process meaning that partial compiling
    is possible for debugging by stopping adding to the chain of transitions in
    the process.

    The general use case to create a process is as follows
    myProcess = (Process("myProcess")
                 >> myFirstComponent.firstTransition
                 >> myFirstComponent.secondTransition
                 >> mySecondComponent.firstTransition
                 >> mySecondComponent.secondTransition)

    However, the adding of new methods does not need to happen only at the
    initialization of the Process class. The above example can be added to as
    follows:
    myProcess >> myThirdComponent.firstTransition
    myProcess >> myThirdComponent.secondTransition

    In general once all the transition methods are added to the process there
    are two ways of actually running the transitions defined in the process.
    The first is through the use of myProcess.pure(current_state, **kwargs) this
    executes the process as a pure method doing nothing to update the actual
    state of the model.

    The other method for running a process is through
    myProcess.execute(**kwargs). This runs the process with the current state of
    the model. By default, this also does not update the model with the final
    state, however this can be changed with the flag "update_state".
    """
    def __init__(self, name):
        """
        Creates an empty process using the provided name

        Args:
            name: the name of the process (should be unique per context)
        """
        self._method = None
        self._calls = []
        self.name = name
        self._needed_args = set([])
        self._needed_contexts = set([])

        cc = get_current_context()
        if cc is not None:
            cc.register_process(self)

    @staticmethod
    def make_process(process_spec, custom_process_klass=None):
        """
        Used in the creation of a process from a json file. Under normal
        circumstances this is not normally to be called by the user.

        Args:
            process_spec: the parsed json object to create a process from

            custom_process_klass: a custom subclass of a process to build

        Returns: 
            the created process
        """
        if custom_process_klass is None:
            custom_process_klass = Process
        newProcess = custom_process_klass(process_spec['name'])

        for x in process_spec['calls']:
            path = x['path']
            ctx = infer_context(path)
            component_name = path.split("/")[-1]
            newProcess >> getattr(ctx.get_components(component_name), x['key'])
        return newProcess

    @property
    def pure(self):
        """
        Returns: 
            the current compile method for the process as a pure method
        """
        return self._method

    def __rshift__(self, other):
        """
        Added wrapper for the transition method.

        Args:
            other: the transition call for the transition method

        Returns: 
            the process for the use of chaining calls
        """
        return self.transition(other)

    def transition(self, transition_call):
        """
        Adds the given transition call to the Process. The argument call must be
        decorated by the @transition decorator.

        Args:
            transition_call: transition method to add to the process

        Returns: 
            the process for the use of chaining calls
        """
        self._calls.append({"path": transition_call.__self__.path, "key": transition_call.resolver_key})
        self._needed_contexts.add(infer_context(transition_call.__self__.path))
        new_step, new_args = compile_component(transition_call)

        for arg in new_args:
            self._needed_args.add(arg)
        self._method = compose(self._method, new_step)
        return self

    def execute(self, update_state=False, **kwargs):
        """
        Executes the process using the current state of the model to run. This
        method has checks to ensure that the process has transitions added to it
        as well as if all of the keyword arguments required by each of the
        transition calls are in the provided keyword arguments. By default, this
        does not update the final state of the model but that can be toggled
        with the flag "update_state".

        Args:
            update_state: should this method update the final state of the model?

            **kwargs: the required keyword arguments to execute the process

        Returns: 
            The final state of the process regardless of the model is updated to 
            reflect this. Will return null/None if either of the above checks fail
        """
        if self._method is None:
            warn("Attempting to execute a process with no transition steps")
            return
        for arg in self._needed_args:
            if arg not in kwargs.keys():
                warn("Missing kwarg", arg, "in kwargs for Process", self.name)
                return
        state = self.pure(self.get_required_state(include_special_compartments=True), **kwargs)
        if update_state:
            self.updated_modified_state(state)
        return state

    def as_obj(self):
        """
        Returns: 
            Returns this process as an object to be used with json files
        """
        return {"name": self.name, "class": self.__class__.__name__, "calls": self._calls}

    def get_required_args(self):
        """
        Returns: 
            The needed arguments for all the transition calls in this process as a set
        """
        return self._needed_args

    def get_required_state(self, include_special_compartments=False):
        """
        Gets the required compartments needed to run this process, important to
        note that if this is going to be used as an argument to the pure method
        make sure that the "include_special_compartments" flag is set to True so
        that special compartments found in certain components are visible.

        Args:
            include_special_compartments: A flag to show the compartments that
                denoted as special compartments by ngcsimlib (this is any
                compartment with * in their name, these are can only be created
                dynamically)

        Returns: 
            A subset of the model state based on the required compartments
        """
        compound_state = {}
        for context in self._needed_contexts:
            compound_state.update(context.get_current_state(include_special_compartments))
        return compound_state

    def updated_modified_state(self, state):
        """
        Updates the model with the provided state. It is important to note that
        only values that are required for the execution of this process will be
        affected by this call. If all of the compartments need to be updated, view
        other options found in `ngcsimlib.utils`.
        
        Args:
            state: the state to update the model with
        """
        Set_Compartment_Batch({key: value for key, value in state.items() if key in self.get_required_state(include_special_compartments=True)})


def transition(output_compartments, builder=False):
    """
    The decorator to be paired with the `Process` call. This method does
    everything that the now outdated resolver did to ensure backward
    compatability. This decorator expects the user/developer to decorate a 
    static method on a class.

    Through normal patterns, these decorated method will never be directly called
    by the end user, but if they are for the purpose of debugging there are a
    few things to keep in mind. The process compiler will automatically
    link values in the component to the different values to be passed into the
    method that does not exist if they are directly called. In addition, if the
    method is going to be called at a class level the first value passed into
    the method must be None to not mess up the internal decoration.

    Args:
        output_compartments: the string name of the output compartments the
            outputs of this method will be assigned to in the order they are output.
            builder: A boolean flag for if this method is a builder method for the
            compiler. A builder method is a method that returns the static method to
            use in the transition.

    Returns: 
        the wrapped method
    """
    def _wrapper(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            return f(*args, **kwargs)


        class_name = ".".join(f.__qualname__.split('.')[:-1])
        resolver_key = f.__qualname__.split('.')[-1]


        inner.fargs = f.__func__.__code__.co_varnames[:f.__func__.__code__.co_argcount]
        inner.f = f
        inner.output_compartments = output_compartments

        inner.class_name = class_name
        inner.resolver_key = resolver_key
        inner.builder = builder

        add_component_transition(class_name, resolver_key,
                               (f, output_compartments))

        add_transition_meta(class_name, resolver_key,([], [], [], True))

        return inner
    return _wrapper

