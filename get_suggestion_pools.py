import json

import requests


def get_intents(utterance: str):
    headers = {
        'authority': 'conversation-tooling-d.watsonplatform.net',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'origin': 'https://conversation-tooling-d.watsonplatform.net',
        'x-xsrf-token': 'D7P0LPFE-ifLAu4kjhWJ_ogyvOu8iUql_iEI',
        'x-watson-userinfo': 'bluemix-instance-id=91ea8c36-f81d-4f19-b191-cc580a480f0f;bluemix-region-id=us-south;bluemix-crn=crn:v1:staging:public:conversation-dev:us-south:a/d630482187a7420687bf2e8ba9f1a2d9:91ea8c36-f81d-4f19-b191-cc580a480f0f::',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/79.0.3945.79 Chrome/79.0.3945.79 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'accept': 'application/json, text/plain, */*',
        'x-global-transaction-id': '69335bc6-af83-4bfa-80df-1d7575be54c3',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://conversation-tooling-d.watsonplatform.net/us-south/crn:v1:staging:public:conversation-dev:us-south:a~2Fd630482187a7420687bf2e8ba9f1a2d9:91ea8c36-f81d-4f19-b191-cc580a480f0f::/skills/27c4b01c-5f92-48f0-9b47-3f438e96a549/build/intents',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,cs;q=0.8',
        'cookie': 'cd_user_id=16feca7b62d12a-0eae5b5a5a6c06-24414032-384000-16feca7b62e3a8; notice_preferences=2:; notice_gdpr_prefs=0|1|2:; cmapi_gtm_bl=; cmapi_cookie_privacy=permit_1|2|3_; optimizelyEndUserId=oeu1580223416098r0.3681616348452126; ajs_group_id=null; ajs_user_id=%22IBMid-50YTYC81B4%22; ajs_anonymous_id=%2250YTYC81B4%22; _hjid=9a71ddc1-81c2-4ccd-a113-dd04a15a82e3; optimizely-user-id=1thcywh5oq5; kampyle_userid=0df2-7a89-715c-30c3-6b89-23cb-f2aa-970f; mdigital_alternative_uuid=6ab1-a320-76c8-f688-c432-a018-e2f2-0da6; lp-sync-16520780-vid=YyMTZlYmY0YTYyYmI0NDdh; JSESSIONID=s%3AWK3GtNOtDUwr388t7D5RyXOvKoH3DooF.w8njzyZH4kKKnT3EbU33903a%2FWmUV3NQX9LV95mNqqg; notice_behavior=expressed|eu; _hjIncludedInSample=1; kampyleUserSession=1580680890711; kampyleUserSessionsCount=3; cm-pill-events={%22hasSlideInAnimated%22:true%2C%22hasCollapseAnimated%22:true}; kampyleSessionPageCounter=3; lp-sync-16520780-sid=yDQPk7hSSx6NfpgXUT6KGA; XSRF-TOKEN=D7P0LPFE-ifLAu4kjhWJ_ogyvOu8iUql_iEI',
    }

    params = (
        ('nodes_visited_details', 'true'),
    )

    data = '{"input":{"text":"' + utterance + '"},"context":{"conversation_id":"dfd90e3a-b267-40b8-9e62-f250ac9811f7","system":{"initialized":true,"dialog_stack":[{"dialog_node":"root"}],"dialog_turn_counter":1,"dialog_request_counter":1,"_node_output_map":{"node_8_1482956046487":[0],"node_1_1538425354688":[0]},"branch_exited":true,"branch_exited_reason":"completed"},"timezone":"Europe/Prague","mycredentials":{"user":"47062333-9e52-4b16-96bb-565a332ddaa6","password":"LxdnMHmKF3eFPg44yb42g6nhUYEk2b8wZcMGM9dV1Y95ZJHuHJGs7I1kZsdexZg3"}},"alternate_intents":true}'

    response = requests.post(
        'https://conversation-tooling-d.watsonplatform.net/rest/v1/workspaces/27c4b01c-5f92-48f0-9b47-3f438e96a549/message',
        headers=headers, params=params, data=data)

    intents = json.loads(str(response.content, "utf-8"))["intents"]
    return intents


with open("utterances.json", "r") as file:
    data = json.load(file)

utterance_intents = {}

for utterance in data["disambiguation"] + data["no_disambiguation"]:
    intents = get_intents(utterance)
    utterance_intents[utterance] = intents

with open("utterance_to_intents.json", "w") as file:
    json.dump(utterance_intents, file)
