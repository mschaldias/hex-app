# ToDoHex

## **Web App**
https://todohex.onrender.com/

##  Features
- Drag-and-Drop Interface: move tasks between todolists and todolists between boards.
- Task Management: set due date and recurring task options.
- Week View: plan your week with dedicated backlog, futurelog and weekly todolists.
- Weekly Migration: move into the next week, tasks are automatically assigned to the backlog and week day todolists.
- Hexed Tasks: pick a random task from the backlog and complete it by the end of the day to increase your hex score.
- Account Management: register and activate account, reset password or delete account.
- REST API: provides access to an authenticated user's board, todolist and task resources.


### **Local setup**
#### **Pip:**
`pip install -r requirements.txt`

#### **Conda:**
`conda env create --name env --file=environment.yml`

### **Database migrations**
    python manage.py makemigrations
    python manage.py migrate

### **Run**
`python manage.py runserver`
### **Technologies**:
 - Django, Django REST
 - Bootstrap5
 - Javscript, JQuery
 - SQLite3, PostgreSQL 15
 
