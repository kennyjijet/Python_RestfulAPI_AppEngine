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
5. Call getmyitems action with uuid to get list of items in user inventory, this action will also
   process the item progression (item status). if item is a resource producer type, Its status will
   turn to 'produced' when it ready to give resource. Now this item is waiting for user to collect 
   its produced resource.
6. Call event action with $(evid)=Collect and $(inid)=WhateverItemInventoryID. This action will grap
   produced resource from item to user and clean item, start producing from 0 again.
PS. resource refers to gold, oil, fuel, tyres, and so on
