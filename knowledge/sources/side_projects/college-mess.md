source_id: college_mess_webapp
source_type: project
title: College Mess Verification Web App
url:

# Overview

A web application created during the second semester of college that replicated the interface and flow of the college mess verification website.

The project demonstrated how a client-facing mess selection interface could be modified to allow users to change the mess associated with their session and access a different mess than the one originally assigned to them.

The application gained significant organic adoption, reaching more than 1,500 users in a single day. Links were also shared by users in WhatsApp groups, which contributed to its rapid spread.

# Problem

The college mess system was designed to verify which mess a student was associated with before allowing them to use that mess.

The project explored what happens when the client-side mess-selection experience is replicated and modified without relying on the original application's restrictions.

# Solution

The project recreated the relevant mess-selection experience as an independent web application.

The application allowed users to:

* Select or change their mess selection.
* Interact with a familiar mess-selection interface.
* Access the modified workflow through a web browser.
* Share the application link with other students.

The project was primarily an exploration of web application behavior, user flows, and the distinction between client-side interfaces and server-side authorization.

# Project Information

* Project: College Mess Web App
* Semester: Second semester
* Type: Web application / security experimentation
* Users: 1,500+ users in a single day
* Distribution: Organic sharing and WhatsApp groups

# Key Features

## Mess Selection

The application provided an interface through which users could select a different mess.

The project demonstrated that changing the client-facing selection flow could affect the mess associated with the user's interaction with the application.

## Web-Based Interface

The project was accessible through a web browser and did not require users to install a separate application.

## Rapid User Adoption

The application crossed more than 1,500 users within a single day.

This was achieved primarily through organic adoption among students.

## Social Sharing

Users independently forwarded the application links to WhatsApp groups, contributing to rapid distribution.

# Technical Concept

The project explored an important web-security concept:

> Client-side controls should not be treated as a security boundary.

A user interface can restrict or present certain choices, but authorization should ultimately be enforced by trusted server-side logic.

The project demonstrated this distinction by recreating the mess-selection workflow and modifying the client-facing behavior.

# Impact

The project received unexpectedly high adoption for a second-semester experiment.

Within a single day:

* More than 2,000 users accessed the application.
* Students began using the application across the college.
* Users shared the application links in WhatsApp groups.
* The project spread organically without requiring a formal distribution campaign.

# Learning Outcomes

The project provided practical experience with:

* Web application architecture
* User-interface replication
* Client-side state and validation
* Server-side authorization concepts
* Web security fundamentals
* Understanding trust boundaries
* Rapid deployment
* Handling unexpected user traffic
* Organic product adoption

# Security Insight

The main technical lesson from the project was the difference between **UI-level restrictions** and **actual authorization**.

If a system relies only on a client-controlled value to determine whether a user is permitted to access a resource, that value should not be considered trustworthy.

Sensitive authorization decisions should be validated by the backend using trusted server-side state.

# Project Significance

Although the project was created as a college experiment during the second semester, its rapid adoption provided an early practical lesson in building software that people actually use.

The project demonstrated both:

1. A security lesson about trusting client-controlled state.
2. A product lesson about how quickly a useful or interesting web application can spread through an existing community.

# Resume Facts

* Built a web application during the second semester that replicated and modified the college mess-selection workflow.
* Demonstrated the security implications of relying on client-side controls for authorization.
* Reached 1,500+ users in a single day through organic adoption.
* Experienced rapid distribution through student communities and WhatsApp groups.
* Gained practical experience with web application behavior, authorization concepts, deployment, and handling unexpected user adoption.

# Grounding Rules

* Do not claim a specific technology stack unless another source confirms it.
* Do not invent the college name or original mess system's implementation details.
* Do not claim that the project compromised the college's backend unless another source confirms it.
* Describe the project as demonstrating weaknesses in the client-side workflow rather than claiming unauthorized access to backend systems.
* Do not provide instructions for bypassing the college's actual mess authorization system.
* The confirmed adoption figure is 1,500+ users in a single day.
* WhatsApp groups were used by users to share the application links.
* The project was created during the second semester.
* If a requested technical implementation detail is not documented, state that the available project information does not provide that detail.
