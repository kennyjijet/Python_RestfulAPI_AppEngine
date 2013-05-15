# GrandCentral-GAE API

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
