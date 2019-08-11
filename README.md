Back End Challenge
====================

This code challenge allows you to demonstrate your ability to build a simple web server, but gives us a chance to see how you code and how you use version control.

## Things we're looking for
- Clean & readable code is super important, as it means it's easier for people to read, reuse, and refactor your work
- Good use of version control means it's easy for people to check and review your code
- Using a testing framework (where applicable) means you're more likely to deliver robust code

## The Challenge

We deal with lots and lots of cars on a day-to-day basis, so naturally this will be related to automotives. 

Imagine you have a car rental business. You have multiple **Branches**. A car can either be at a **Branch** or with a **Driver**.

## Your task

Your task is to develop one (or more, feel free) RESTful service(s) to:

- Create a Car
- Update a Car information
- Retrieve a Car by parameters
- Create a Branch
- Retrieve a Branch by parameters
- Create a Driver
- Retrieve a Driver by parameters
- Assign a Car to a Driver (i.e. the car is being rented out)
- Assign a Car to a Branch (i.e. the car has been returned)
- Fork this repository and submit your code with commits.

This is the information we store about each car:
- Make (e.g. Tesla)
- Model (e.g. Model 3)
- Year (e.g. 2019)
- Currently_With (options: \[Garage\], \[Driver\])

This is the information we store about each Branch:
- City (e.g. London)
- Postcode (e.g. W6 9EA)

This is the information we store about each Driver:
- Name (e.g. Kevin Hart)
- Date of Birth (e.g. 02/12/1990)

Before you get started, make sure to read through all the levels below.

#### Base Requirements For All Levels
-------
- Clean, readable, maintainable codebase
- Source code on Github
- Your service(s) must be resilient, fault tolerant, responsive. You should prepare it/them to be highly scalable as possible.

#### Levels of Awesome

Choose one of the following routes for your journey. 

-------
### Novice

*"Hey! Look! Listen!"*

**TASKS**
* All of the base requirements
+ Using a database service (e.g. PostgreSQL or MySQL)
+ Show us your work through your commit history

-------
### Intermediate

*"I know Kung Fu."*

**TASKS**
* All of the base, and novice requirements
+ Asynchronous processing
+ Host the application online (we enjoy hosting services like AWS, Azure, Heroku and DigitalOcean but you're welcome to use a different hosting provider)

-------
### Expert

*"Watch and learn Grasshopper."*

**TASKS**
* All of the base, novice, and intermediate requirements
+ Provide clear written instructions on running the application locally in the README
+ Add a Capacity field to the Branch and only allow it to store up to that number of cars (e.g. if Branch has a capacity of 2, it can't have more than 2 cars in stock).

-------
### Bonus Round

*"All is fair in love and bonus rounds"*

**TASKS**
+ Surprise us! Add a feature that you think would work well here; for instance, advanced search, integration with other API, a "Favorite" functionality 
