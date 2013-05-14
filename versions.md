# GrandCentral-GAE API

## 14 May 2013 
- Optimize and write comments to hardpurchase action class

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
