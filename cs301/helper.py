from typing import Optional,Callable, Any,List
import datetime
import mongoengine
import bson


class Owner(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    facultyid = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    Department = mongoengine.StringField(required=True)
    doj = mongoengine.StringField(required=True)
    publication = mongoengine.ListField()
    grants = mongoengine.ListField()
    awards = mongoengine.ListField()
    teaching = mongoengine.ListField()

    meta = {
        'db_alias': 'chor',
        'collection': 'owners'
    }





def create_account(name, email, background, publications, grants, awards, teaching) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.Department = background
    owner.publication = publications
    owner.grants = grants
    owner.awards = awards
    owner.teaching = teaching
    owner.save()
    return owner

def create_account_by_flask(fid,name, password,dept, email,doj) -> Owner:  
       
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.Department = dept
    owner.password = password
    owner.facultyid =fid
    owner.doj = doj
    owner.save()
    return owner


def deletePublication(fid, pub):
    Owner.objects(facultyid = fid).update_one(pull__publication=pub)

def deleteGrants(fid, pub):
    Owner.objects(facultyid = fid).update_one(pull__grants=pub)
    
def deleteAwards(fid, pub):
    Owner.objects(facultyid = fid).update_one(pull__awards=pub)
    
def deleteTeaching(emailid, pub):
    Owner.objects(facultyid= emailid).update_one(pull__teaching=pub)
    
def deleteMiss(emailid, pub):
    Owner.objects(email = emailid).update_one(pull__miss=pub)
    

def addPublication(fid, pub):
    Owner.objects(facultyid = fid).update_one(push__publication=pub)

def addGrants(fid, grant):
    Owner.objects(facultyid = fid).update_one(push__grants=grant)

def addAwards(fid, awards):
    Owner.objects(facultyid= fid).update_one(push__awards=awards)

def addTeaching(fid, teach):
    Owner.objects(facultyid = fid).update_one(push__teaching=teach)


def find_account_by_fid_and_password(facultyid: str, password: str) -> Owner:
    owner = Owner.objects(facultyid=facultyid, password = password).first()
    return owner


def find_account_by_fid(facultyid: str) -> Owner:
    owner = Owner.objects(facultyid=facultyid).first()
    return owner







