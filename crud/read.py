from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
from threading import Thread
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import literal
from sqlalchemy import and_
from werkzeug.security import generate_password_hash,check_password_hash
import sys
from flask import jsonify
sys.path.insert(0, '../models/')


from models import Base,User,Filedetails
import datetime


engine = create_engine('sqlite:///crud/beeruva.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

def listofilesuploaded(currentuser):
    """
    Function to return list of files uploaded by a user.
    """
    session=DBSession()
    files=session.query(Filedetails).filter_by(userid=currentuser.userid)
    listoffiles=[]
    for i in files:
        filedata={}
        filedata['fileid']=i.fileid
        filedata['parentid']=i.parentid
        filedata['filename']=i.filename
        filedata['filetype']=i.fileextension
        filedata['Upload date']=i.fileuploadedon
        listoffiles.append(filedata)
    return jsonify(listoffiles)

def getchildren(folderid, currentuser):
    """
    Function to return list of files under given folder.
    """
    session=DBSession()
    files=session.query(Filedetails).filter_by(parentid=folderid)
    listoffiles=[]
    for i in files:
        filedata={}
        filedata['fileid']=i.fileid
        filedata['filename']=i.filename
        filedata['parentid']=i.parentid
        filedata['fileext']=i.fileextension
        filedata['filetype']=i.filetype
        filedata['Upload date']=i.fileuploadedon
        listoffiles.append(filedata)
    return jsonify(listoffiles)

def getdescendents(folderid, currentuser):
    """
    Function to return list of all files under given folder.
    """
    files=u_getdescendents(folderid)
    listoffiles=[]
    for i in files:
        filedata={}
        filedata['fileid']=i.fileid
        filedata['parentid']=i.parentid
        filedata['filename']=i.filename
        filedata['fileext']=i.fileextension
        filedata['filetype']=i.filetype
        filedata['Upload date']=i.fileuploadedon
        listoffiles.append(filedata)
    return jsonify(listoffiles)

def u_getdescendents(folderid):
    """
    Function to return list of files uploaded by a user.
    """

    try:
        session = DBSession()

        res = session.query(
                    literal(folderid).label("fileid"),
                    literal(None).label("parentid"),
                    literal('d').label("filetype")
                ).cte(recursive=True, name="res")

        R = res.alias()

        res = res.union_all(
                    session.query(
                        Filedetails.fileid,
                        Filedetails.parentid,
                        Filedetails.filetype
                    ).join(
                        R,
                        and_(
                            R.c.fileid == Filedetails.parentid,
                            R.c.filetype == 'd'
                        )
                    )
                )

        res = session.query(Filedetails).join(res, and_(Filedetails.fileid == res.c.fileid, res.c.fileid != folderid));

        return res.all()
    except Exception as err:
        print err
        return []

def check_access(fileid,currentuser):
    """
    Function to check users access to the requested file.
    """
    session=DBSession()
    returnfiledata={}
    try:
        filedata=session.query(Filedetails).filter_by(userid=currentuser.userid).filter_by(fileid=fileid).one()
        returnfiledata['fileid']=filedata.fileid
        returnfiledata['filename']=filedata.filename
        returnfiledata['access_state']=1
        return returnfiledata
    except NoResultFound:
        returnfiledata['access_state']=0
        return returnfiledata
