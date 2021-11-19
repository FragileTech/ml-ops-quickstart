"""
This is mostly a copy paste from \
https://github.com/pallets/click/blob/2fc486c880eda9fdb746ed8baa49416acab9ea6d/src/click/termui.py

Modified to allow prompt input that has a different color than the prompt text, while keeping
the color of the default prompt values the same as the prompt text color.
"""  # noqa: D400
import io

from click.exceptions import Abort, UsageError
from click.types import Choice, convert_type
from click.utils import echo, LazyFile


# The prompt functions to use.  The doc tools currently overwrite these
# functions to customize how they work.
visible_prompt_func = input

_ansi_reset_all = "\033[0m"


def hidden_prompt_func(prompt):
    """Input hidden text from the user."""
    import getpass

    return getpass.getpass(prompt)


def _build_prompt(text, suffix, show_default=False, default=None, show_choices=True, type=None):
    prompt_ = text
    if type is not None and show_choices and isinstance(type, Choice):
        prompt_ += f" ({', '.join(map(str, type.choices))})"
    if default is not None and show_default:
        prompt_ = f"{prompt_} [{_format_default(default)}]"
    return f"{prompt_}{suffix}"


def _format_default(default):
    if isinstance(default, (io.IOBase, LazyFile)) and hasattr(default, "name"):
        return default.name

    return default


def prompt(
    text,
    default=None,
    hide_input=False,
    confirmation_prompt=False,
    type=None,
    value_proc=None,
    prompt_suffix=": ",
    show_default=True,
    err=False,
    show_choices=True,
) -> None:
    """Prompts a user for input.  This is a convenience function that can \
    be used to prompt a user for input later.

    If the user aborts the input by sending a interrupt signal, this
    function will catch it and raise a :exc:`Abort` exception.

    .. versionadded:: 7.0
       Added the show_choices parameter.

    .. versionadded:: 6.0
       Added unicode support for cmd.exe on Windows.

    .. versionadded:: 4.0
       Added the `err` parameter.

    :param text: the text to show for the prompt.
    :param default: the default value to use if no input happens.  If this
                    is not given it will prompt until it's aborted.
    :param hide_input: if this is set to true then the input value will
                       be hidden.
    :param confirmation_prompt: asks for confirmation for the value.
    :param type: the type to use to check the value against.
    :param value_proc: if this parameter is provided it's a function that
                       is invoked instead of the type conversion to
                       convert a value.
    :param prompt_suffix: a suffix that should be added to the prompt.
    :param show_default: shows or hides the default value in the prompt.
    :param err: if set to true the file defaults to ``stderr`` instead of
                ``stdout``, the same as with echo.
    :param show_choices: Show or hide choices if the passed type is a Choice.
                         For example if type is a Choice of either day or week,
                         show_choices is true and text is "Group by" then the
                         prompt will be "Group by (day, week): ".
    :return: None
    """
    result = None

    def prompt_func(text):
        f = hidden_prompt_func if hide_input else visible_prompt_func
        try:
            # Write the prompt separately so that we get nice
            # coloring through colorama on Windows
            echo(f"{text}{_ansi_reset_all}", nl=False, err=err)
            return f("")
        except (KeyboardInterrupt, EOFError):
            # getpass doesn't print a newline if the user aborts input with ^C.
            # Allegedly this behavior is inherited from getpass(3).
            # A doc bug has been filed at https://bugs.python.org/issue24711
            if hide_input:
                echo(None, err=err)
            raise Abort()

    if value_proc is None:
        value_proc = convert_type(type, default)

    prompt_ = _build_prompt(text, prompt_suffix, show_default, default, show_choices, type)

    while 1:
        while 1:
            value = prompt_func(prompt_)
            if value:
                break
            elif default is not None:
                value = default
                break
        try:
            result = value_proc(value)
        except UsageError as e:
            if hide_input:
                echo("Error: the value you entered was invalid", err=err)
            else:
                echo(f"Error: {e.message}", err=err)  # noqa: B306
            continue
        if not confirmation_prompt:
            return result
        while 1:
            value2 = prompt_func("Repeat for confirmation: ")
            if value2:
                break
        if value == value2:
            return result
        echo("Error: the two entered values do not match", err=err)


def confirm(
    text,
    default=False,
    abort=False,
    prompt_suffix=": ",
    show_default=True,
    err=False,
) -> bool:
    """Prompts for confirmation (yes/no question).

    If the user aborts the input by sending a interrupt signal this
    function will catch it and raise a :exc:`Abort` exception.

    .. versionadded:: 4.0
       Added the `err` parameter.

    :param text: the question to ask.
    :param default: the default for the prompt.
    :param abort: if this is set to `True` a negative answer aborts the
                  exception by raising :exc:`Abort`.
    :param prompt_suffix: a suffix that should be added to the prompt.
    :param show_default: shows or hides the default value in the prompt.
    :param err: if set to true the file defaults to ``stderr`` instead of
                ``stdout``, the same as with echo.
    :return: User's decision.
    """
    prompt_ = _build_prompt(text, prompt_suffix, show_default, "Y/n" if default else "y/N")
    while 1:
        try:
            # Write the prompt separately so that we get nice
            # coloring through colorama on Windows
            echo(f"{prompt_}{_ansi_reset_all}", nl=False, err=err)
            value = visible_prompt_func("").lower().strip()
        except (KeyboardInterrupt, EOFError):
            raise Abort()
        if value in ("y", "yes"):
            rv = True
        elif value in ("n", "no"):
            rv = False
        elif value == "":
            rv = default
        else:
            echo("Error: invalid input", err=err)
            continue
        break
    if abort and not rv:
        raise Abort()
    return rv
