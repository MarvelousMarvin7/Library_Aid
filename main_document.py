#!/usr/bin/env python3
"""Main script to test the application"""

from datetime import datetime, timedelta
from models import storage
from models.abstract import Abstract
from models.classification import Classification
from models.document import Document
from models.notification import Notification
from models.query import Query
from models.research import ResearchSession
from models.tag import Tag
from models.user import User


# Creation of a User
user = User(email="test1@gmail.com", user_name="Test Me",
             password="testpwd", image_url="/static/images/users/test_pic.jpeg", is_institution_user=True)
user.save()

# Creation of a document
document_1 = Document(user_id=user.id, title="Infs 311 past questions", file_type="PDF", file_path="/static/documents/infs 421.pdf",
                    image_url="/static/images/doc/test.jpeg", classification_code="QD78",
                      abstract="This document contains past questions for Infs 421")
document_1.save()

document_2 = Document(user_id=user.id, title="Infs 429 past questions", file_type="PDF", file_path="/static/documents/infs 429.pdf",
                    image_url="/static/images/doc/test.jpeg", classification_code="TD7",
                     abstract="This document contains past questions for Infs 429")
document_2.save() 

# Creation of research session
start_time = datetime.utcnow()
end_time = start_time + timedelta(hours=2)
research_session = ResearchSession(user_id=user.id, session_start=start_time, session_end=end_time)
research_session.save()

research_session.documents_accessed.append(document_1)
research_session.documents_accessed.append(document_2)

# Creation of a querry
query = Query(user_id=user.id, 
              document_id=document_1.id,
              research_session_id=research_session.id, 
              query_text="What is Information systems?", 
              response_text="Information systems blabla bla test me.")
query.save()


# Creation of notification
notification = Notification(user_id=user.id, message="You have a new notification", is_read=False)
notification.save()

#creation of abstract
abstract = Abstract(document_id=document_1.id, abstract_text="This is an abstract for the document")
abstract.save()

#Creation of classification
# -------------------------
# Create a parent classification
parent_classification = Classification(
    document_id=document_2.id,
    name="Technology",
    category_code="TECH",
    description="Topics related to technology."
)
parent_classification.save()

# Create a child classification
child_classification = Classification(
    document_id=document_2.id,
    name="Artificial Intelligence",
    category_code="TECH_AI",
    description="Topics related to AI.",
    parent_id=parent_classification.id
)
child_classification.save()

# tag creation
tag1 = Tag(tag="AI")
tag2 = Tag(tag="Research")
tag3 = Tag(tag="Technology")

tag1.save()
tag2.save()
tag3.save()

# Associate tags with the document
document_2.tags.extend([tag1, tag2, tag3])
document_2.save()

storage.save()

print("\nUser:")
users = storage.all(User).values()
for user in users:
    print(f"ID: {user.id}, Email: {user.email}, Name: {user.user_name}, Institution User: {user.is_institution_user}")

# Fetch and display documents
print("\nDocuments:")
documents = storage.all(Document).values()
for doc in documents:
    print(f"ID: {doc.id}, Title: {doc.title}, Tags: {[tag.tag for tag in doc.tags]}")

# Fetch and display queries
print("\nQueries:")
queries = storage.all(Query).values()
for query in queries:
    print(f"ID: {query.id}, User ID: {query.user_id}, Document ID: {query.document_id}, Text: {query.query_text}, Response: {query.response_text}")

# Fetch and display research sessions
print("\nResearch Sessions:")
sessions = storage.all(ResearchSession).values()
for session in sessions:
    print(f"ID: {session.id}, User ID: {session.user_id}, Start: {session.session_start}, End: {session.session_end}")
    print("Accessed Documents:")
    for doc in session.documents_accessed:
        print(f" - {doc.title}")

# Fetch and display notifications
print("\nNotifications:")
notifications = storage.all(Notification).values()
for notif in notifications:
    print(f"ID: {notif.id}, User ID: {notif.user_id}, Message: {notif.message}, Is Read: {notif.is_read}")

# Fetch and display abstracts
print("\nAbstracts:")
abstracts = storage.all(Abstract).values()
for abstract in abstracts:
    print(f"ID: {abstract.id}, Document ID: {abstract.document_id}, Text: {abstract.abstract_text}")

# Fetch and display classifications
print("\nClassifications:")
classifications = storage.all(Classification).values()
for classification in classifications:
    print(f"ID: {classification.id}, Name: {classification.name}, Code: {classification.category_code}, Description: {classification.description}, Parent ID: {classification.parent_id}")

# Fetch and display tags
print("\nTags:")
tags = storage.all(Tag).values()
for tag in tags:
    print(f"ID: {tag.id}, Tag: {tag.tag}")

print("All test finished")