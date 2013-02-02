
# insulaudit

Homepage: https://github.com/bewest/insulaudit

This python package provides a toolkit for dealing with data used and
created by a "modern," circa 2010, insulin therapy regimen.

We provide a command line text based tool, and a python
library to audit therapeutic data from a variety of
medical devices widely used.

## Target Devices
  * Medtronic Minimed Paradigm Series insulin pumps
    using the usbstick

    * observed working with a 522

  * Lifescan Glucose Meters:

    * Onetouch series
    * Mini/Profile

  * Dexcom, Onetouch Ping, Bayer, omnipod.  In no particular order.

  * Bayer, coming soon: thanks to iko, https://bitbucket.org/iko/glucodump/src/e37ea2a38776/glucodump/usbcomm.py

## Usage

```bash

  insulaudit [opts] [command]
  insulaudit <device> [opts] [command]
  insulaudit [device] [command] [opts]

  insulaudit --help
  insulaudit clmm scan


```

### Lifescan
Nothing special, my system registers a serial device right
away.

### Minimed
In linux, you need to poke the usbserial module with some
parameters to make it work.  This only needs to be done
once::
  
    sudo modprobe usbserial vendor=0x0a21 product=0x8001
    # or
    sudo ./reset.sh
    # which runs ./remove.sh and ./insert.sh, the latter
    # of which does the modprobe for you.

I've observed runs working up to 5 times in a row, at
which point I needed to reset the usbstick by removing it
and re-inserting into the PC.
On mac, I can't recall if this is necessary.  We just need
a generic usb-serial adapter.  I haven't tried it, but I
suspect COM1 will likely work on M$, although
auto-scanning will not detect it.  If your mac inserts the
device somewhere under `/dev/usb.serial*` we will likely
scan it.

In dmesg, you should see a message like this when you
inser the usb stick::
  
    [201197.513266] usb 2-1: new full speed USB device using uhci_hcd and address 3
    [201197.919110] usb 2-1: configuration #1 chosen from 1 choice
    [201205.729621] usbcore: registered new interface driver usbserial
    [201205.730808] USB Serial support registered for generic
    [201205.731143] usbcore: registered new interface driver usbserial_generic
    [201205.731145] usbserial: USB Serial Driver core
    [201205.806220] USB Serial support registered for pl2303
    [201205.806248] pl2303 2-1:1.0: pl2303 converter detected
    [201208.305166] usb 2-1: pl2303 converter now attached to ttyUSB0
    [201208.305187] usbcore: registered new interface driver pl2303
    [201208.305189] pl2303: Prolific PL2303 USB to serial adaptor driver
    bewest@mimsy:~/Documents/bb/diabetes/src/mock$ 

# Installing insulaudit
There is no official release of insulaudit, only some pieces of code
towards establishing a tool.  Pull requests welcome.

:::
   
    # Download the source
    # https://github.com/bewest/insulaudit
    # or fork it on github
    git clone http://github.com/bewest/insulaudit.git
    # install insulaudit in your python runtime so you can
    # hack on it from here
    python setup.py develop

# Status quo

As [Thucydides said](http://en.wikipedia.org/wiki/Thucydides)
> Right, as the world goes, is only in question between
> equals in power, while the strong do what they can and
> the weak suffer what they must.

## [decoding-carelink](https://github.com/bewest/decoding-carelink)
Medtronic is partially decoded.  We will be adding support to
insulaudit when things are better/tested and cleaned up.  Have a
Medtronic pump?  Help us analyze the data, and visualizations are that
much closer.  At this point, we just need people to help line up
records with the CSV output, and confirm accuracy or highlight
problems.

## [decoding-omnipod](https://github.com/bewest/decoding-omnipod)
Need captures/traces.

## [decoding-dexcom](https://github.com/bewest/decoding-dexcom)
Need captures/traces.

## [decoding-onetouchping](https://github.com/bewest/decoding-onetouchping)
Need captures/traces.


# How to run (outdated)

The commands using PYTHONPATH assume you are in the root
directory of the repo.
The commands using insulaudit assume you have installed
insulaudit on your system (including the develop version).

Uses flaky port scanning feature to test if we are able to
talk to a pump.  Exchange a few bytes, nothing more::
     
    # fails
    PYTHONPATH=src/ python -m insulaudit.main -v clmm   hello
    insulaudit -v clmm hello

Specifying a port seems to work.  If it doesn't, retry a
few times. ::
    
    # using the subcommand stuff:::
    PYTHONPATH=src/ python -m insulaudit.main -v clmm --port /dev/ttyUSB0  hello
    insulaudit -v clmm --port /dev/ttyUSB0 hello
    
    # run the protocol exercise directly
    PYTHONPATH=src/ python src/insulaudit/devices/clmm/proto.py /dev/ttyUSB0
    python -m insulaudit.devices.clmm.proto.py /dev/ttyUSB0

    # read-pump-model.log - protocol exercise to read pump
    model number.  Log of it running successfully 5 times
    before it starts failing.  stderr and timestamps were
    not capture. :-(

# TODO
Now that the basic framework is taking shape, the protocol
support needs to be stabilized and the framework needs to
continue to gel a bit.


  * convert hello to some kind of scan
  * introduce new device flows
  * introduce device profiles/console flows
  * record logs
  * review logs
  * audit logs

    * merge logs
    * search
    * reformat

##cli tool insulaudit
  * init - set up a config, from default
  * checkPort/scan - scan for a port/device
  * device

    * profile
    * log 


::
  

## License
Author
  Ben West <bewest+insulaudit@gmail.com>

This experimental software is provided under the `MIT
license`_, so you can do with it whatever you wish except
hold me responsible if it does something you don't like.

.. _MIT license: http://www.opensource.org/licenses/mit-license.php

Blather
-------
http://www.diabetesmine.com/2013/01/the-ethical-imperative-of-diabetes-interoperability.html

Interoperability is my middle name.  Just give us the raw data, and
we'll make it interoperable.

# Fidelity of Care

Patients need open access to all the elements of
technology involved in therapy in order to ensure safety.

One of many concrete examples involves generating safe
insulin doses.  The vendor hard coded the active lifetime
of insulin into all models earlier than the 515 series.
This guarantees that patients receive the wrong amount of
insulin.  The only feasible way of getting safer doses of
insulin is to buy a pump in the 515 series or newer.
Users who do choose to buy a new pump can customize this
variable but the variable remains static and mostly
incorrectly calibrated until it's manually changed again.
In reality, your sensitivity to insulin varies, and the
amount of insulin one should receive also varies
dramatically throughout the day depending on what life
throws your way.

However, the pump has an administrative protocol that
allows software to automatically audit logs, reconfigure
settings, create and administer dosing schedules.  If
users had access to this protocol we could use it to work
around bugs like incorrect insulin calibrations in order
to tune our doses.  We can also use the protocol to audit
the logs, allowing us to independently verify that pump
therapy is safe.

There are many other examples where having direct access
to all the technology involved in therapy provides an
epistemic certainty integral to basic science.  As
patients and users of medical technology, we want to
believe that it is safe.  The only way to do this is to
empirically study all the relevant details of vendor
technology with our peers and to study it for bugs and
safety.  In the process of doing this we discovered that
the same commands used to audit the native therapeutic
logs can also be used to reconfigure the device, and
administer insulin in ways that can work around bugs that
are currently ensuring unsafe dosing for pump users.

The manufacturer is content to give me inaccurate dosings,
but refuses to share information about the protocol needed
to quickly, safely and independently manage my therapy.
As patients we need access to all the technology in our
therapy so that we can have epistemic certainty that it is
safe.

We set out to use the protocol in order to audit logs more
effectively and found out it's possible to generate safer
doses and work around bugs in vendors' therapeutic
software.  The protocol is actively kept from our use, but
we need it in order to secure safe therapy.  Without
having investigated the technology involved in our
therapy, we cannot believe it is safe, and we would not
have learned about it's true capabilities.

### Thought exercises
If a doctor approached you with a syringe, said you needed
some of it but wasn't personally sure a.) how much was in
the syringe, that b.) the syringe sometimes injects the
wrong amount, and c.) what contents of the syringe might
due to the way the syringe performs, but that someone told
him this would probably be "ok" would you allow yourself
to be injected?  What if the consequences for refusing the
syringe was death?  What if the reason for the uncertainty
was because someone had wiped off most of the calibration
markings before giving it to the doctor to fill?  What if
the person who had wiped off the markings was the same
person insisting it was safe and selling you the syringes,
and no one else makes syringes?

For the argument "Most users won't need access to
technology to get what they need."  This isn't an argument
for preventing patients from accessing critical parts of their
own therapy.  This is like arguing no one would need to do
anything more than borrow a book from a library shortly
after the printing press because the population was
unlettered and homes lacked bookshelves to house the
books.
# Blather
## "Blah blah blah."

Diabetes therapy is wasteful, unscientific, and dangerous.
Despite a variety of companies offering software to manage
the condition, very little data is used to drive real time
decision making during the course of therapy.  Many users
take error prone and time consuming handwritten
transcriptions of their devices, because the software
provided is incapable of communicating or managing
therapeutic details in any useful way.  Some users
actually take pictures, and upload those pictures to
websites, finding that the easiest way to share critical
therapy data.

Despite all the hard work diabetics undertake in efforts
audit and control ongoing therapy, most use a variety of
mobile devices that automatically log many details.
In 2011, we have a nascent highly connected world where
relationships construct a social graphs traversable on
the web with enough security to trust these relationships
for authentication.  Despite all the technical
advancement in our world, the medical community asks
diabetic patients to live inhumane lives maintaining open
wounds while blaming them for lack of control and failing
to explain cause and effect.

Insulin is a powerful drug best administered by a
pancreas.  When we use a syringe to inject a large dose
all at once, it is no surprise to see dangerous
consequences.  However, instead of developing ever
increasingly accurate predictions, the use of software in
managing diabetes mostly involves entering and massaging
lots of data.  As a result, many diabetics suffer
needlessly, blamed for the effect "their condition" has on
them due to their poor control, even though the
consequences are likely aggravated or caused by the very
therapy they are trying to participate in.  This is poor
fidelity of care.

The best example for this is the NPR obituary for a
baseball hall of famer who died of diabetic complications.
While he was praised for his adherence to his regimen, he
was also praised his tenacity on the field, despite the
terrible shakes attributed to "his condition."  However,
they failed to mentioned that the shakes he suffered were
due to the therapy for his condition; the only way a type
1 diabetic suffers shakes like that is when too much
insulin has been delivered, an all too familiar mishap.
Poor fidelity of care is not knowing what to expect,
despite adhering to a therapy.

By applying the fundamentals of the scientific method to
therapy, and to the application of technology to therapy,
we get a unique perspective on what the technology should
do, and the role people have in therapy.
The only data we should be entering are corrections on what we
predict will happen.  This is  be one of the ideal
applications of technology to therapy through a lense I
call high "fidelity of care." Together, we adjust our
expectations to match what is possible so that over time
the observations of therapy exactly match the expectations
we recorded as predictions earlier.

As we integrate calendar data and predictions along side
past observations, we get a better understanding of causes
and effects in the outcomes of our own therapy while
gaining tools to communicate these understandings with our
therapeutic team, composed of any individual we choose.
The therapeutic team may well be mostly composed of
members outside the medical community, because social
support is often important in maintaining habits and
lifestyle.

This meta observation of the delta between hypothesis and
empirical data is a principle component of the scientific
method, but entirely absent from therapeutic software,
leading to a dearth in fidelity of care.  My hope is that
insulaudit can help to increase the fidelity of care.  The
scientific method involves recording high fidelity
observations, making predictions based on that data,
performing an experiment, and then analyzing the
differences between the observations and the expectations.
Therapy should not be any different.  However, until we
can get transparent access to audit the raw data produced
by our therapy, we cannot get an accurate perspective of
our own health.

Therefore, the first fundamental principle of high
fidelity care is open access to all the intimate details
of therapeutic care in as close to the native format as
possible.  It includes access to the protocols
transporting the data, so that novel applications can
augment therapeutic fidelity in ways unforeseen by the
original makers, for the benefit of the patient, and their
caregivers.

The second is peer review.  A caregiver may be a friend,
or even a good samaritan in a time of need, who needs
instructions on what to do next.  A caregiver may be a
researcher who needs access to data for simulations.  It
includes access to the firmware, because it is outrageous
that the software that governs lives has not gone through
open source review for bugs and safety.

With these in place, safe and effective from insulaudit,
SMART, DUBS, GCCS, and many other collaborators can help
infuse therapeutic practice with high fidelity care.
The needs of the patient in the practice of high fidelity
care are not unique to diabetics.  We believe all patients
will benefit from the application of these principles
throughout their care.

~ [insulaudit collaborators](https://github.com/bewest/insulaudit/network/members) 
