# Galah

**Documentation for galah.api available at https://galah-api.readthedocs.org/en/latest/!**

## What is Galah?

Galah is a teaching utility that automatically analyzes students' code as
they create it and provides feedback to both the students and the instructors.
It does this by continually running tests on students' code aand providing the
results to both the instructors and the students.

Professors are responsible for creating test harnesses for their assignments,
aside from that Galah does the rest of the work: running those tests inside of
a secure VM; consolidating results into a database; and providing an interface
for the students and teachers to see the results of the testing.

## License

Licensed under the GPLv3. When I get around to it I will stick licensing
notices all over the place.i

## Credit and Contributors

For now this will contain all the contributors and credits due as it is a small
list. It may move to a proper COLLABORATORS.txt file or some other device
later.

Thank you all of you!

### Ben Kellogg

Helped considerably with galah.sheep, wouldn't have been able to finish it
without him.

### UCR Staff & Faculty

Victor Hill, Kris Miller and Brian Linard have all been
enormously helpful in getting Galah off the ground and into production.
That's not even mentioning the other staff and faculty at UCR who have
shared their knowledge with me. Thank you everyone who has helped me grow
as a software engineer.

Victor Hill was also the one who initially conceived of Galah, I just
implemented it.

### Christopher Johnson

Has a very nice site at www.chris.com that I got some ASCII birds from. I would
like to grab some more in the future so the error pages can generate a random
ASCII bird every time you go them. Now error pages are fun too!

### Chris Manghane

Implemented Galah's support for Google OAuth2.


## News

### Monday, June 25, 2012

Changing version scheme to something a little less ridiculous. I don't really
know what my version scheme was before but now I'll follow more standard
conventions. MajorVersion.MinorVersion.Patch[rc#], in other words what you'd
expect. I will refer to the previous release 0.1beta1 as 0.1rc1 from now on.
The next "release" will be 0.1rc2. When I feel confident that a lot of the
bugs are worked out we'll release 0.1.

Each component of Galah is pretty distinct and decoupled from the other
componenets of Galah but I don't want to make multiple repositories for each
unless each one grows very large in size (which they shouldn't), so there
won't be seperate versioning for each component.

### Sunday, June 24, 2012

Version 0.1beta1 has been released. This release contains only galah.web and
galah.db running without support for interacting with the testing backend. All
functionality needed for deploying in a production environment is there and
most of it is documented.

Exciting day today :).
