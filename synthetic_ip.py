from Xlib import X, display, protocol
import time

time.sleep(3)
WINDOW_ID = 0x5c00001
x = 1000
y = 1234

d = display.Display()
w = d.create_resource_object('window', WINDOW_ID)

event = protocol.event.ButtonPress(
    time=0,
    root=d.screen().root,
    window=w,
    child=X.NONE,
    root_x=0,
    root_y=0,
    event_x=x,
    event_y=y,
    state=0,
    detail=1,
    same_screen=1
)

w.send_event(event, propagate=True)
d.sync()

event = protocol.event.ButtonRelease(
    time=0,
    root=d.screen().root,
    window=w,
    child=X.NONE,
    root_x=0,
    root_y=0,
    event_x=x,
    event_y=y,
    state=0,
    detail=1,
    same_screen=1
)

w.send_event(event, propagate=True)
d.sync()