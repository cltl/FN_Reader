# FrameNet input to tool

This directory contains two files:
* **lu_to_frames.json**
* **frame_to_info.json**

The files in this directory are created using:
https://github.com/cltl/FN_Reader/blob/master/tool_utils.py

## **lu_to_frames.json**

In this current version, a **lemma** is mapped to its candidate frame IDs according to FrameNet 1.7, e.g.,

```json
"sail": [
    "64",
    "65",
    "690"
],
"sailor": [
    "2670"
],
```

## **frame_to_info.json**

In this current version, a frame ID is mapped to its definition, and role information, e..g,
```json
"9": {
    "definition": "This frame characterizes states-of-affairs with Protagonists in relations with each other that may be viewed symmetrically.  When the Protagonists are equally prominent, each equally serving to identify the others, they are expressed together as Protagonists.  When one of the Protagonists serves to define the other (more or less as a Ground), it is called Protagonist_2, and the other is called Protagonist_1 (i.e. the Figure). '' This frame exists as a background for a number of lexical frames, including Chatting, Similarity, Exchange, and Being_attached.  The most basic frames inheriting from this one are symmetrical states.  (For example, Being_attached is symmetrical, since if A is attached to B, B is attached to A.)   '' Other frames exhibiting reciprocality either have a causative/inchoative relation to such a stative frame (e.g. Becoming_attached), or are stative-like summarizations of multiple events of the same kind.  This second type, in which events are performed reciprocally, with two equal participants acting on each other, can be exemplified by the Chatting frame in which two people are effectively both speakers and addressees in a joint act of communication.  '' The basic characteristic of this frame, inherited in the daughters, is the equivalence of Protagonist_1 + Protagonist_2 to Protagonists, and the further equivalence (modulo figure/ground profiling) of the following: '' Protagonist_1 Relation with Protagonist_2. '' Protagonist_2 Relation with Protagonist_1. '' Protagonists Relation.",
    "roles": [
        {
            "role_definition": "The particpant in a reciprocal event that is encoded as the subject of an active-form sentence or as a by-PP in a passive. `'You can't argue politics with foreigners,' sighed the policeman.' ",
            "role_id": 33,
            "role_type": "Core"
        },
        {
            "role_definition": "The participant in a reciprocal event that is coded in a with-PP. 'We have been arguing the point with the inspector at claims branch for many many months and we just seem to go round in circles. '",
            "role_id": 34,
            "role_type": "Core"
        },
        {
            "role_definition": "The jointly expressed participants in a reciprocal activity. 'They were gossiping about the weather and American football.' ",
            "role_id": 35,
            "role_type": "Core"
        }
    ]
},
```

## Considerations
* do we use the part of speech in the look-up and if so NAF or Universal Dependencies?
* what kind of identifiers do we use for FrameNet lexical units, roles, and frames? Framester or other one.
* how do we vizualize the information to the annotators? Which information do we show?