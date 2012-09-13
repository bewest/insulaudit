
# Advocacy

## What do we want?

We want to verify the safety and efficacy of our therapy.  We want to
ensure that the therapy we use is based on science, and that findings
and analysis can be reproduced at will for peer review.

The easiest way to do this is not to iterate on focus-group driven
marketing checklists, but by allowing users to access the information
needed to investigate, debug, audit, and review the behavior of their
devices.  This means we need access to the protocols used to
communicate with the medical device.

Here is an example of a document from Lifescan that educates a code
literate person to talk with their glucometer:
https://github.com/bewest/diabetes/blob/master/lifescan/OneTouchUltra2Protocol.pdf

## What will we do with this information?

We will build tools to record raw data representing the ongoing
behavior and configuration settings of devices, and analyze it.  We
will also build tools to independently reproduce analysis required to
produce a medical report.  This reproduction is required in order to
peer review and contrast with the vendor's analysis, and to verify
that the device is operating as expected.

In addition, with this information under patient control, the patient
can also integrate with third party solutions, such as Fitbit, or MS
Vault, or some other secure, distributed, personal storage locker yet
to be invented, even when the vendor's marketing or legal department
decides not to integrate useful or safer features.

In our research to verify the accuracy of the analysis the vendors
provide we discovered that there were hazardous situations that clever
control of these devices through the protocol could help avoid.  For
example, the calculation of insulin on board could be moved to a
browser session, or a smart phone/tablet where personalized software
could compute the most accurate doses in collaboration with your
medical team.  This would allow users to work around issues like
incorrectly hard-coded variables used as inputs to important dosing
functions.  In other words, allowing users to access the full range of
protocol commands could help them get safer therapy by working around
vendor issues, designed or otherwise.  Insulin on board is only one
easy example where user access to the protocol actually affects
and ensures safety.

## What about the liability?

Everyone who crosses a street is personally responsible for "looking
both ways" before crossing.  In the same way, everyone who uses a
medical device is responsible for maintaining their own safety,
regardless of the errors they introduce.  For example, the FDA has
documented 1,500+ injuries
http://www.fda.gov/ForHealthProfessionals/ArticlesofInterest/ucm295562.htm
and 13 deaths over a ten year study that are ongoing due to user
experience issues.  Since the pump is working as designed, it was
theoretically possible to avoid the hazardous conditions encountered
if the user had been able to give the pump proper instructions.

However, the work flow as designed by the vendor discourages critical
analysis, and has is also documented by the FDA in the hazards chart
http://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/GuidanceDocuments/ucm206153.htm#8
in section 6H Table 8, as encouraging habituation of overrides that
easily lead to ignoring important warnings.

So where is the liability on the vendors for the current batch of
hazardous events?  Since they control the user experience, are they
not responsible for the harm incurred by the experiences typified by
an inability to confirm if the right amount of insulin had been given?

What we're advocating is to make the operation of the pump better
reviewed in order to make it possible to improve the user experience.
Patients are always responsible for adhering to safe therapy, since
they are the drivers in their own empiric experience.

So there is no new liability in allowing users to inspect the
technical details, they are in fact vital to properly understanding
therapy, to enable proper record keeping, and in order to reproduce
and verify the vendor's analysis.  It's also the only way to ensure
vendor patents on safe algorithms don't threaten safety, as they
currently do.  Who is responsible for that?

It's unethical to hold me responsible for harm that is currently
ensured by the work flow controlled by the vendor, due to hard coding
variables, etc, without allowing me any way to monitor it.  This is
kind of like handing me a syringe after wiping off all the calibration
markings, or blind folding me before instructing me to cross the
street.  In the course of attempting to monitor it, I found it was
possible to avoid harm altogether if only I was allowed access to the
right information.  Who is liable for that?

However, if we do start analyzing data from real people, and we find
that the devices are actually misbehaving, or not behaving as
advertised, I suppose this would be a new, or exposed liability for
vendors.  An objection on these grounds would be surprising, because
the technology has allegedly been deemed as safe by their own tests
and through the FDA approval process.

## But you are a novice and will mess up

I have no confidence in my personal ability to write excellent and
clean code.  I do have confidence in scientific methods, involving the
review of my friends and colleagues, and the internet at large.  I'm
convinced with the right community organized, there is a set of
uniquely qualified people who can create a set of royalty-free safe
technology that is easy to use and monitor.  The vendors mess up too,
we've found numerous questionable during our code base, setting aside
the "open" nature of the protocol as described by security hacker
Jeromy Radcliffe et al.

The technology to do this is not magic just poorly reviewed.  Keeping
it poorly reviewed won't increase safety.

## But you are advanced user, what about all the intermediate users

As mentioned earlier, they currently have no tools to personally and
independently audit their data.  If I die because of one of the
hazardous situations mentioned by the FDA, and it was in fact
impossible to avoid because of habituation or some frankly mysterious
pump behavior, it's still user error.  Users are always on the hook
for using the device correctly if it is in fact working as designed.

Our tools will help determine if the pump is working as designed.
There's no need for access to this technology to be any more difficult
than using a website such as Facebook or Gmail, and will allow authors
and patients to integrate with services they choose in order to
keep in touch with their doctor.  The intermediate users are in danger
without tools to properly audit their therapy.

I haven't proposed changing the device as designed, merely allowing us
to independently reproduce analysis of the behavior, and to
independently control the device.  We bought an insulin pump, and I
fail to see why our use of it should be limited to a design dictated
by an FDA clinical study that doesn't match my body.  The golden rule
for this type of therapy is: "the right drug, at the right rate, at
the right time, for the right patients."

Using tools to audit and monitor expectations of device therapy is
much better than constantly guessing, and habituating to dangerous
conditions.

## Don't you have access to data?

No.  In scientific parlance, "having data" means that you should be
able to independently reproduce experiments or analysis given a set of
observations.  When several independent groups have reproduced an
analysis, then this aids our [epistemic
certainty](http://plato.stanford.edu/entries/certainty/) that the
knowledge being communicated is correct.  Medtronic offers a very
limited portal which is time consuming to use, and difficult to set
up.  However most importantly, it fails to provide enough data to
independently reproduce the findings and analysis they present.  There
is no way to verify the accuracy or analysis of the information
they've presented, but there is a wide surface area for bugs to
inflict damage from where the data originated.  The media has
documented cases where bugs in this space [caused incorrect diagnosis
and loss of user data in other
situations](http://blogs.wsj.com/cio/2012/07/20/philips-recalls-flawed-patient-data-system/).

If I don't have enough information to reproduce the analysis as
offered by the salesman, then how can I ask for a second opinion?  How
can I verify its accuracy?

The [scientific process for discovering
knowledge](http://en.wikipedia.org/wiki/Scientific_method#Confirmation)
requires that they make this information available.  The FDA
guidelines also recommend documenting the communications interfaces,
the network protocols, remote functions, and pump logs.  It's
exceedingly puzzling that the vendors refuse to do comply.

It turns out that if we did have access to the protocol, a range of
useful capabilities from better communication of therapeutic progress,
to security, to working around dangerous hazards are also obtainable,
but not without the data to reconstruct and audit a pump's behavior.

## What is a user error?

http://en.wikipedia.org/wiki/Use_error
If the device is working "as designed" it means that is capable of
correctly executing the programming it's been given.  Hazards that are
not user error are things like the battery explodes or leaks, or the
motor malfunctions, or an electric shock disables the system.
Otherwise, if the device is operating, any hazardous condition that
exists as a result of the machine working is then a user error.

For example, if I give you an interface with two buttons, red and
green, such that they switch colors back and forth.  I can design the
rate or the behavior of the UI such that you will never be able to
press a green button.  If I tell you to only press a green button, and
make it impossible but tempting to attempt pressing the green button,
and you wind up pressing a red button, we will call that user error.
If I offer you a control to stop the switching, then you can
successfully complete the task.  But whether or not the task was
possible, it's user error, regardless of how likely you were to
succeed.

The FDA guidance for insulin pumps documents the dangers associated
with forcing users to habituate to overrides without adequate tools to
personally audit and communicate expectations.  This is not a
marketing problem, but a basic safety problem, fixable by including the
protocol documentation in the user manual.  Many companies, especially
TV manufacturers do this already.

The fact that the device was working as designed when these hazardous
conditions occurred only underscores the importance of making the
behavior of these devices transparent and "debuggable" by the people
using them.
