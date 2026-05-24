# Nice blog
A simple blogging server. Simply start the server and have an ```articles``` directory right next to it. The server uses flask, for public deployment it is recommended to use ```waitress``` or other servers, instead of ```flask run```. Articles must have a unique title and be in this format: 
```md
---
title: Some nice Title
date: YYYY-MM-DD
---
Your article goes here
```
Putting this in your directory will automatically update the blog. 
To change the appareance, edit the html files. 

## ToDos
- Deleting articles is not supported right now. Will be supported in the future.
