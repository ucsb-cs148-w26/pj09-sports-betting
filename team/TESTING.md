# Testing Demo: Jest

When designing a unit test, we decided to use Jest. This is because research showed that Jest was the most documented and was recommended in past offerings of CS 148.

## Units to Test: useGameData

We decided to test our useGameData implementation. useGameData connects to a websocket from our backend and receives updates on all current gamestates. It then passes these updates to the game components to create a realtime updating display. We thought it best to test this to ensure that the websocket was handling connections gracefully and that it was able to process both good and bad data accordingly. 

## Testing Implementation 

We wrote 3 unit tests for this file. One to test live updates, one to test websocket errors, and one to test http errors. To do this, we needed to create a mock websocket that would send data in a predictable yet stable pattern to assert that it worked. We also created a non-opening mock websocket to demonstrate what would happen if the websocket connection never happened. 

## Result
We ensured these unit tests passed to assert our implementation worked. 