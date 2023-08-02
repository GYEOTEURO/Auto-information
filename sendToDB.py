import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd



# Use the application default credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# autoInformation(collection) - 카테고리명(doc) - posts(collection) - 개별 post(doc)

doc_ref = db.collection(u'autoInformation').document(u'{csv 파일에서 가져온 카테고리명}')

# 유의미한 ID를 두지 않고 Cloud Firestore에서 자동으로 ID를 생성 : add()
doc_ref.collection("posts").add({
    u'title': None,
    u'content': None,
    u'original_link': None,
    u'content_link': None,
    u'image': None,
    u'region': None,
    u'date': None,
    u'site' : None,
    u'disabillity_type': None,
})