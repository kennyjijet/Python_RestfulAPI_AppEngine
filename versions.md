# GrandCentral-GAE API

## 16 May 2013
### Item Sequence Processing
1. Call getsoftstore action with uuid to get list of items that user can purchase
2. Call softpurchase action with itid(retrieved from getsoftstore) to purchase $(itid)item
3. $(itid)item will add to user's inventory but hold status as 'pending' until reach deliver time
4. When the item reachs the deliver time, its status will turn to 'reward' and 'rewarded'
   The differences of 'reward' and 'rewareded' is that item's status will 'reward' only one time 
   after changed from 'pending'. Client is able to know that the item has just rewarded so client
   can perform popup, special effect, or whatever. And then the status 'reward' will turn to 'rewarded'
   and never turn back to 'reward' again.
5. (Optional) If player doesn't want to wait until reach deliver time. Call finishnow action with uuid, and inid.
   this action will take platinum and finish/deliver immediately.
6. Call getmyitems action with uuid to get list of items in user inventory, this action will also
   process the item progression (item status). if item is a resource producer type, Its status will
   turn to 'produced' when it is ready to give resource. Now this item is waiting for user to collect 
   its produced resource.
4. Call event action with $(evid)=Collect and $(inid)=WhateverItemInventoryID. This action will grap
   produced resource from item to user and clean item, set item's status back to 'rewareded', 
   start producing from 0 again. user can do collecting only when item's statis is 'produced'.
   PS. 'resource' refers to gold, oil, fuel, tyres, and so on

## 15 May 2013
Store game data to single one database instead of storing separately. 
For instance, Storeitem and event data deployed from Google Drive Custom-Backend will store in the same database, 
instead of storing them separately. 
This will reduce duplication code in the project.

The GAS Test system is setup, you can see test result in google drive.
If you have any test want to add, please contact me for consulting or do it for you.

Next update will release in version 2

## 14 May 2013 
- Optimize and write comments to hardpurchase action class
- Combine deployitem and deployevent classes into one deploy class

## 13 May 2013
- An option to get specific player's states (partials) 
For instance, /loadplayer?uuid=xxxxx&specific=xp,gold will return {"xp":1234,"gold":5678}
- Improve resource producing time system, (more consistent with other time system)
- Add comments to code
- Migrate model class helpers from one single 'Core class' to Their own mother class. For instance, Core.getplayer() changed to Player.getplayer() etc.
- Improve and optimize some minor code.

## 9 May 2013
- Implement deduct and collect behaviours
- Add fuel, fuel_max, xp to player state

## 8 May 2013
- Add support for multiple api version running simultaneously
- Implement event call for 'reward' behaviour

## 7 May 2013

- Re-structed item json object
- Add deployevent action for deploying event's data from Drive
- Add event action to be called from client
