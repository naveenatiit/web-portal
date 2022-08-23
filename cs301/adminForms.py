from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField

from wtforms import validators, ValidationError

class adminWorks(Form):
   Table = RadioField('Table',[validators.Required("Please enter \
      your choice.")] , choices = [('fac','Faculty table'),('hod','Hod table'),
      ('crossC','Cross cutting table'),('leaveH','Leave hierarchy table'),
      ('proj','Project table'),('copi','Co PI table'),
      ('app_hier','App hierarchy table'),('agency','Agency table')])
   
   
   Opt = SelectField('Operation', choices = [('I', 'Insert'), ('U', 'update'),('D','Delete')])
   submit = SubmitField("Send")

class facultyTable(Form):
    username = TextField("Employee id ",[validators.Required("Please enter \
      employee id.")])
    
    dept = TextField("Name Of Dept",[validators.Required("Please enter \
      dept name.")])

    submit = SubmitField("Send")

class hodTable(Form):
    username = TextField("Employee id Of Hod",[validators.Required("Please enter \
      employee id.")])
    
    dept = TextField("Name Of Dept",[validators.Required("Please enter \
     dept name.")])

    submit = SubmitField("Send")

class crossCuttingTable(Form):
    username = TextField("Employee id Of CC",[validators.Required("Please enter \
      employee id.")])
    
    desgn = TextField("Name Of Desgn",[validators.Required("Please enter \
     designation name.")])

    submit = SubmitField("Send")

class leaveHTable(Form):
    child = TextField("Name Of child",[validators.Required("Please enter child .")])
    
    parent = TextField("Name Of parent",[validators.Required("Please enter parent.")])
    
    forWhom = TextField("Name Of for whom",[validators.Required("Please enter for whom.")])

    submit = SubmitField("Send")


class projectTable(Form):
    projId = TextField("Proj name",[validators.Required("Please enter Proj name")])
    
    manpower = IntegerField("Manpower budget",[validators.Required("Please enter Manpower budget")])
    
    equip = IntegerField("Equipment budget",[validators.Required("Please enter equipment budget")])

    travel = IntegerField("Travel budget",[validators.Required("Please enter Travel budget.")])

    mainId = TextField("Main PI employee id",[validators.Required("Please enter Main PI employee id")])

    submit = SubmitField("Send")


class copiTable(Form):
    username = TextField("Project id ",[validators.Required("Please enter project id.")])
    
    dept = TextField("Co PI employee id",[validators.Required("Please enter employee id of co pi.")])

    submit = SubmitField("Send")


class agencyTable(Form):
    name = TextField("Agency name",[validators.Required("Please enter agency name")])
    
    manpower = IntegerField("Manpower budget",[validators.Required("Please enter Manpower budget")])
    
    equip = IntegerField("Equipment budget",[validators.Required("Please enter equipment budget")])

    travel = IntegerField("Travel budget",[validators.Required("Please enter Travel budget.")])

    submit = SubmitField("Send")

class appHTable(Form):
    child = TextField("Name Of child",[validators.Required("Please enter child \
      name.")])
    
    parent = TextField("Name Of parent",[validators.Required("Please enter parent\
      name.")])

    submit = SubmitField("Send")