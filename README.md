# tutorialcode
This is an optional base code for Flask and Python.

This database project is the final project for class CMPSC 431W

Two type of users of CanvasPath are: Students and Faculty Members, where Administrator is a special type of staff.
Three parts need to be managed in CanvasPath are: Departments, Courses, Sections, where Capstone section is a special type of section where exams are replaced by Capstone projects. 

Here is the list of requirements and constrains for each users and parts: 

•	Students:

o	Students can only see their own grades

o	Students must be enrolled to at least one class (total participation)

o	A student can enroll to only one section of a course (key constrain)

o	Students can form team for Capstone section; every team can only work on one project (key constrain, total paticipation) and have more than one student (total participation) 


•	Faculty Members:

o	All course sections need to be taught by at least one faulty member (total participation)

o	A faculty member can teach same course in different semester or multiple sections in one semester

o	The faculty member can only manage the courses being taught in current semester

o	Selected faculty members can be sponsor of capstone project; one sponsor can mentor multiple projects


•	Department:

o	Every faculty member belongs to only one department (key constrain, total participation)

o	Every student has to major in at least one department (can have many major) (total participation)


•	Courses: 

o	One courses can only be offered by one department (key constrain, total participation)

o	Some courses can have pre-requisite 


•	Sections:

o	One course can have multiple sections

o	Each Capstone section has exactly one sponsor (key constrain, total participation), but can be performed by different teams (total participation) 

