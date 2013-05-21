# GrandCentral-GAE API

GrandCentral-GAE is a backend application, provides backend services (REST) for gamification, 
built on Google App Engine and using almost everything of Google's infrastructure services.

## Versioning
GC-GAE supports multiple version api(s) running simultaneously. Specify version by add version number prior of url.

<b>For example:</b> <br/>
GC-GAE main url is http://game-punks.appspot.com<br/>
GC-GAE version 1 will be http://1.game-punks.appspot.com<br/>

<b>Version available:</b><br/>
1

## Item Sequence Processing
1. Call getsoftstore action with uuid to get list of items that user can purchase
2. Call softpurchase action with itid(retrieved from getsoftstore) to purchase $(itid)item
3. $(itid)item will add to user's inventory but hold status as 'pending' until reach deliver time
4. When the item reachs the deliver time, its status will turn to 'reward' and 'rewarded'
   The differences of 'reward' and 'rewareded' is that item's status will 'reward' only one time 
   after changed from 'pending'. Client is able to know that the item has just rewarded so client
   can perform popup, special effect, or whatever. And then the status 'reward' will turn to 'rewarded'
   and never turn back to 'reward' again.
5. (Optional) If player doesn't want to wait until reach deliver time. Call finishnow action with uuid, 
   and inid. this action will take platinum and finish/deliver immediately.
6. Call getmyitems action with uuid to get list of items in user inventory, this action will also
   process the item progression (item status). if item is a resource producer type, Its status will
   turn to 'produced' when it is ready to give resource. Now this item is waiting for user to collect 
   its produced resource.
7. Call event action with $(evid)=Collect and $(inid)=WhateverItemInventoryID. This action will grap
   produced resource from item to user and clean item, set item's status back to 'rewareded', 
   start producing from 0 again. user can do collecting only when item's statis is 'produced'.
   PS. 'resource' refers to gold, oil, fuel, tyres, and so on

## Multiple language-content supported
GrandCentral supports multiple languages for text-contents, using the same concept as dictionary.
All words, sentenses, dialogs, narrative, and any text-contents are defined in each language in spreadsheet (Google Drive).
And deploy (using DeployToGAE app script) the spreadsheet to GrandCentral-GAE, and GrandCentral will serve it to users.

<b>For example:</b> <br/>
Game client might want to skin the game in German language, the game will need to grab german-dictionary from GC-GAE
using action 'getdict' (requires two parameters: passwd and lang)
Fetch http://game-punks.appspot.com/getdict?password=....&lang=German
This will respond with list of keys and its text-content in German. 
After client has retrieved dictionary, it should place the text into the postion regarding its key

<b>Supported languages are following:</b> <br/>
English, Spanish, German, French, Italian, SimplifiedChinese, TraditionalChinese, Japanese, Korean, 
Russian, and BrazilianPortuguese
