
# Contributing

## What

## cloud-enabled glucometer

Among other things,
We have a prototype enabling any glucose meter with an accessible serial port
to become an internet-connected device.  Control and audit of the glucose
meter can be performed by a server on the internet, or by services running
close to the user, eg. on the user's phone.  The prototype allows the glucose
meter internet, or link local access, and control through a simple javascript
or python interface through wifi, ethernet, or 3g access.

It's based on beaglebone and node.js.  Basic prototype consists of reverse
port forwarding via ssh the port that tty.js is running on to a location of my
choosing.  From there, I can browse to the "control panel" and run the
insulaudit python scripts to produce log files.  This proof of concept is a
bit of a mind-bender but demonstrates more than enough control for anyone to
build this kind of device using commodity, off-the-shelf parts, available today.

### Parts

#### An embeddable device, running linux

We currently favor the Beaglebone.  The Angstrom distribution, and `open
embedded` build system have been fantastic to work with, and the default
images come primed for this kind of development.

#### A 3g modem

We like the Sierra 3g modems from Ting.  Our needs here are rather modest,
really, 2g will do.  We attempt to dial `*99` and `#777` to establish ppp, so
as long as that works, any modem will likely do.

#### A glucometer

I have implemented Lifescan's protocols.  Agamatrix/Sanofi/iBGStar refused to
share.  Bayer sent me *all* the protocols.  If I have no supported your meter,
tell me which meter, help me arrange access to one (should be easy, they will
likely send me one for free since I test upwards of 20 times per day), and
help me get access to the protocol.  That's it, a few phone calls and emails,
and I will implement your glucometer's protocol as quickly as I can in python,
javascript, or ruby.  The work will be published here as soon as it is
available.

We intend to provide testable code implementing data transfer for as many
medical devices as possible.  They are rather trivial to implement.

#### An insulin pump

Well, I hope you don't need one of these.  But if you are like me, then you do
need one, and you need the data.  We almost have the Medtronic protocol
decoded, but need help.  Some more captures, and we are confident we can
completely control the pump.

I use Medtronic's pump, they refuse to share the data I own with me.  As a
result, we are pursuing all options we can imagine.  Help us capture some more
data, and help us solve this problem once and for all.

We believe that after we can show some modest utility from patients having
control of their devices, that all vendors will be pressured to follow suit.
Please let me know if you disagree.

This is the kind of thing that certain forces have a way of routing around.
If we cannot get existing vendors to work with us to help protect patients,
and put an end to the unnecessary exposure to harm and risk, then someone will
eventually build an open insulin pump.  Making one makes perfect sense, it's
simply a question of who and when.  It will be interesting to see which
happens first.

#### A blood pressure monitor, fitbit

It will be trivial to add support for Omron blood pressure monitor, since the
protocols are known, and the basic framework works the same way.

#### Any other serial device

You may plug in this kind of device to any "legacy" device with an accessible
serial port, in order to get it "up and on the web," available for management.

There is a chicken and egg problem here, in that no broker exists to manage a
suite of such services for specific to domains to arbitrary devices that are
known to fulfil those services.  Many existing devices are trivial to adapt
into internet-enabled, "cloud-managed" devices, we haven't provided any
innovation here except to snap together a few lego blocks in the right way.
You can too.

Without the devices demanding to be managed, there is no one reason to service
a variety of internet enabled devices, and there are few outlets to send the
resulting data for analysis.  Without the services to manage them, the number
of devices that can work this way, remains limited, while commercial interest
naturally prefer to simply build a better mouse trap.  However, the internet
of things is already here, and there is a long tail of devices ready to be
plugged in, ready to enable more mindful use of our technology where it serves
us instead of slaving away for the machines others have designed.

## Writing

We need lots of documents, ranging from technical analysis, to arguments for
getting access to our data.

You can edit the wiki, make a fork and submit patches, or simply use
http://gist.github.com/ and let me know.  I'll find a way to use your
contribution.

We have a mailing list on google groups,
[medevice-users](https://groups.google.com/forum/#!forum/medical-device-users)
and
[insulaudit](https://groups.google.com/forum/#!forum/insulaudit)

### Source code

You will need some basic python experience.  I'm doing my best to provide
libraries that hide many of the nasty and tricky bits of massaging data and
protocols, but the work on decoding is incomplete, and I'm hesitant to add
many features beyond "hello world" until we understand the complete protocol.
Let me know if you disagree with my priorities.  To that end, much of my
progress is halted on getting historical logs of insulin dosings, which is a
puzzle with an incomplete solution, still, `~2012-10-19`.

There are good reasons, seemingly, to implement the protocol in javascript.
While I'm at it, I may stub one out in ruby.  Let me know if this interests
you.

The idea is to have a rich set of test suites to prove and document in
"literate code" that we understand the protocol, and can verify the
observations of therapy.  Once this is done, there are lots of people eager to
run all kinds of math against this data, but we need access, first.

## Who is we?

See [contributors](https://github.com/bewest/insulaudit/network/members) among
many many others.  I (`~bewest`) merely funnel many disparate parts to
synthesize compassionate or lovely things.  My immediate problems are getting
access to my pump data, so that others can write algorithms for us to better
manage by type 1 diabetes, and so that I can communicate with my doctor on my
therapy with high fidelity.  There are many people interested in this type of
activity, for a variety of reasons.

## Using

### Install

```bash
# on beaglebone
opkg install python-modules
opkg install python-setuptools
git clone git@github.com:bewest/insulaudit.git
cd insulaudit
# cross your fingers and let me know if this doesn't work ;-)
python setup.py develop

# You can plug in a lifescan meter and run
insulaudit onetouch hello
# Should respond with serial and firmware version

# terminal 1
npm install tty.js
tty.js
# At this point, if you are "link-local" to your beaglebone, you should be
# able to visit: [beaglebone.local(http://beaglebone.local:8080/) in a
# suitable browser
# Where you can open a new terminal from javascript!? and issue:
insulaudit onetouch sugars

# terminal 2 - forward tty.js somewhere else
ssh -g -R *:8080:127.0.0.1:8080 public.example.com
# Now, visit public.example.com:8080 where you can do the same thing.
```

### Where to send the data?

You wil need to know how to exercise control of how and where to send your
data.  See TODO for more info.

