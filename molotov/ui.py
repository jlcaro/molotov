from functools import partial
from humanize import naturaltime
import urwid


def unhandled(key):
    if key == 'ctrl c':
        raise urwid.ExitMainLoop


palette = [
    ('header', 'white', 'dark gray'),
    ('body', 'black', 'white'),
    ('footer', 'white', 'dark gray')]


def process_box(procid, refresh=None, loop=None):

    def update_box(body, footer, refresh, loop, *args):
        try:
            results = refresh(procid)
        except OSError:
            def _stop(*args):
                raise urwid.ExitMainLoop()

            loop.set_alarm_in(.1, _stop)
            return

        body.set_text(str(results))
        duration = 'Started %s.' % naturaltime(results.howlong())
        footer.base_widget.set_text(duration)
        updater = partial(update_box, body, footer, refresh)
        loop.set_alarm_in(1, updater)

    header = urwid.Padding(urwid.Text('Process [%d]' % procid), left=1)
    header = urwid.AttrWrap(header, 'header')
    body = urwid.AttrWrap(urwid.Text('', align='center'), 'body')
    footer = urwid.Padding(urwid.Text(''), left=1)
    footer = urwid.AttrWrap(footer, 'footer')
    divider = urwid.Divider()
    frame = urwid.Pile([('pack', header), divider, body, divider,
                        ('pack', footer)])

    updater = partial(update_box, body, footer, refresh)
    return frame, updater


def init_screen(procs, updater, loop=None):
    widgets = []
    updaters = []

    for proc in procs:
        partial(updater, proc)
        widget, updating = process_box(proc, updater, loop)
        widgets.append(widget)
        updaters.append(updating)

    main_widget = urwid.GridFlow(cells=widgets, cell_width=35, h_sep=1,
                                 v_sep=1, align='left')
    main_widget = urwid.Filler(main_widget, 'top')

    if loop is not None:
        loop = urwid.AsyncioEventLoop(loop=loop)

    urwid_loop = urwid.MainLoop(
            main_widget,
            palette,
            event_loop=loop,
            unhandled_input=unhandled,
    )
    for updating in updaters:
        urwid_loop.set_alarm_in(1, updating)
    return urwid_loop
