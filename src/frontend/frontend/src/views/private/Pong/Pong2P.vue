<script setup lang="ts">

import { Vector3, Color, Mesh } from 'three';
import { onMounted, onBeforeUnmount, ref } from 'vue';
import ThreeService from '../../../services/pong/ThreeService';
import Player from '../../../services/pong/Objects/Player';
import Sphere from '../../../services/pong/Objects/Sphere';
import DashedWall from '../../../services/pong/Objects/Text/DashedWall';
import Score from '../../../services/pong/Objects/Text/Score';
import HelpText from '../../../services/pong/Objects/Text/HelpText';
import GameOver from '../../../services/pong/Objects/Text/GameOver';
import Wall from '../../../services/pong/Objects/Wall';
import { handleCollisions } from '../../../services/pong/Objects/Utils/Utils';
import FontService from '../../../services/pong/Objects/Text/FontService';
import LuckySphere from '../../../services/pong/Objects/LuckySphere';

import {
  dateStart,
  ballGeometry,
  ballGeometry2,
  vecHorizWall,
  ballVelocity,
  bounds
} from '../../../services/pong/Objects/Utils/pongVariables'
import { BIT_FONT, MONTSERRAT_FONT } from '../../../services/pong/Objects/Utils/pongVariables'

const props = defineProps({
  players: Array<Object>,
});

const emit = defineEmits(['gameOver']);

// Extract initial players for the current game
let player1Name = ref(props.players[0].player);
let player2Name = ref(props.players[1].player);

const three = new ThreeService(window.innerWidth, window.innerHeight);

// Ball object
const ball = new Sphere(ballGeometry, new Color('white'), new Vector3(0, 0, 0), ballVelocity, bounds);

// Horizontal walls
const horizWallUp = new Wall(vecHorizWall, new Vector3(0, 10, 0), new Color('white'))
const horizWallDown = new Wall(vecHorizWall, new Vector3(0, -10, 0), new Color('white'))

const luckySphere = new LuckySphere(ballGeometry2, new Color('yellow'));

let wallMid: DashedWall; // Vertical dashed wall
let scorePlayer1: Score;
let scorePlayer2: Score;
let helpText: GameOver;

let helpTextSpace: HelpText;
let helpTextPlayerOne: HelpText;
let helpTextPlayerTwo: HelpText;

let helpTextControlsOne: HelpText
let helpTextControlsTwo: HelpText

let finalScore: GameOver;

async function loadFont() {
  await FontService.loadFont('./src/assets/fonts/Bit5x3_Regular.json').then((loadedFont) => {
    const font = loadedFont;

    // Vertical dashed wall
    wallMid = new DashedWall("- - - - - - - -", new Color('green'), new Vector3(0, 0, -1), font);
    scorePlayer1 = new Score(numScorePlayerOne, new Color('white'), new Vector3(-2, 7.5, 0), font);
    scorePlayer2 = new Score(numScorePlayerTwo, new Color('white'), new Vector3(2, 7.5, 0), font);
    helpText = new GameOver('You', new Color('white'), new Vector3(-15.5, 3.5, 0), font);

    // Set the text for the controls
    helpTextControlsOne = new HelpText(
      'W\n\n\n\n\nS',
      new Color('white'),
      new Vector3(-16, 0, 0),
      BIT_FONT,
      1
    )
    helpTextControlsTwo = new HelpText(
      '↑\n\n\n↓',
      new Color('white'),
      new Vector3(16, 0, 0),
      MONTSERRAT_FONT,
      1
    )

    helpTextSpace = new HelpText('Press space to start', new Color('white'), new Vector3(0, 3.5, 0), BIT_FONT, 1);

    // Set text for the player names
    helpTextPlayerOne = new HelpText(
      player1Name.value,
      new Color('blue'),
      new Vector3(-16, 5.5, 0),
      BIT_FONT,
      1
    )
    helpTextPlayerTwo = new HelpText('AI', new Color('red'), new Vector3(16, 5.5, 0), BIT_FONT, 1)

    finalScore = new GameOver('', new Color('white'), new Vector3(0, 0.5, 0), font);
  });
}

// Player objects (to be initialized later)
let player: Player
let player2: Player

// Scores
let numScorePlayerOne = 0;
let numScorePlayerTwo = 0;

const isAnimating = ref(true)
const isGameOver = ref(false)
const winner = ref('')

// Initialize players with the provided names
player = new Player(
  new Vector3(0.4, 3, 0.5),
  new Color('red'),
  new Vector3(16, 0, 0),
  'ArrowUp',
  'ArrowDown',
  player1Name.value
)
player2 = new Player(
  new Vector3(0.4, 3, 0.5),
  new Color('blue'),
  new Vector3(-16, 0, 0),
  'KeyW',
  'KeyS',
  player2Name.value
)

function setHelpText() {
  helpTextPlayerOne.updateScore(player1Name.value)
  helpTextPlayerTwo.updateScore(player2Name.value)
  three.addScene(helpTextSpace.get())
  three.addScene(helpTextPlayerOne.get())
  three.addScene(helpTextPlayerTwo.get())
  three.addScene(helpTextControlsOne.get())
  three.addScene(helpTextControlsTwo.get())
  setTimeout(() => {
    three.removeScene(helpTextPlayerOne.get())
    three.removeScene(helpTextPlayerTwo.get())
    three.removeScene(helpTextSpace.get())
  }, 3000)
  setTimeout(() => {
    three.removeScene(helpTextControlsOne.get())
    three.removeScene(helpTextControlsTwo.get())
  }, 6000)
}

function setupScene() {
  setHelpText();

  three.addScene(horizWallUp.get());
  three.addScene(horizWallDown.get());
  three.addScene(wallMid.get());

  three.addScene(player.get());
  three.addScene(player2.get());
  three.addScene(ball.get());
  three.addScene(scorePlayer1.get());
  three.addScene(scorePlayer2.get());
  three.addScene(luckySphere.get());

  isAnimating.value = false
}

function update() {
  if (!isAnimating.value) return;
  let isTaken : boolean = true;

if (Date.now() % 5000 < 50) {
  luckySphere.randomizePosition();
  three.addScene(luckySphere.get());
  isTaken = true;
}

if (isTaken) {
  if (ball.getVelocity().x < 0) {
    isTaken = luckySphere.update(ball, player2);
  } else {
    isTaken = luckySphere.update(ball, player);
  }
  if (isTaken)
    three.removeScene(luckySphere.get());
  isTaken = false;
}
  
  player.update();
  player2.update();
  handleCollisions(ball, player, player2);
  let check = ball.update();
  if (check) {
    if (check === 1) {
      numScorePlayerTwo += 1;
      scorePlayer2.updateScore(numScorePlayerTwo);
      blinkObject(scorePlayer2.get());
      if (numScorePlayerTwo == 1) {
        console.log(`${player.getName()} lost!`);
        endGame(player2.getName());
      }
      ball.invertVelocity()
    } else if (check === 2) {
      numScorePlayerOne += 1;
      scorePlayer1.updateScore(numScorePlayerOne);
      blinkObject(scorePlayer1.get());
      if (numScorePlayerOne == 1) {
        console.log(`${player2.getName()} lost!`);
        endGame(player.getName());
      }
    } else {
      console.error('Unexpected check value')
    }
    returnObjectsToPlace()
    const ballVectorY = Math.random() * 0.2 - 0.1
    ball.setVelocityY(ballVectorY)
    isAnimating.value = false
    return
  }

}

// Blinking effect for the score when a player loses
function blinkObject(mesh: Mesh) {
  let visible = true
  const blinkDuration = 800
  const blinkInterval = 200

  const intervalId = setInterval(() => {
    visible = !visible
    mesh.visible = visible

    setTimeout(() => {
      clearInterval(intervalId)
      mesh.visible = true
    }, blinkDuration)
  }, blinkInterval)
}

function returnObjectsToPlace() {
  ball.returnToPlace();
  player.returnToPlace();
  player2.returnToPlace();
}

let debounceTimeout: number | undefined;

function toggleAnimation(event: KeyboardEvent) {
  if (isGameOver.value) {
    return;
  }

  if (event.code === 'Space') {
    // Clear the previous timeout if the event is fired repeatedly
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }

    // Set a delay before executing the function to avoid multiple triggers
    debounceTimeout = window.setTimeout(() => {
      isAnimating.value = !isAnimating.value;
      console.log(`Animation ${isAnimating.value ? 'resumed' : 'paused'}`);
    }, 100); // Adjust the timeout as needed (100ms here)
  }
}

const endGame = (winningPlayer: string) => {
  window.removeEventListener("keydown", toggleAnimation);
  three.removeScene(luckySphere.get());
  finalScore.updateScore(winningPlayer + ' wins!');
  three.addScene(finalScore.get());
  blinkObject(finalScore.get());
  setTimeout(() => {
    finalScore.updateScore('Returning to home...')
  }, 2000)
  setTimeout(() => {
    winner.value = winningPlayer;
    isGameOver.value = true;

    let players = [player1Name.value, player2Name.value];
    let scores = [numScorePlayerOne, numScorePlayerTwo];
    let ids = [props.players[0].id, props.players[1].id];
    const dateEnd = Date.now() / 1000;
    let playersHits = [player.getHits(), player2.getHits()];

    // Emit the tournament data to the parent component
    emit('gameOver', {
      winner: winningPlayer,
      player_names: players,
      player_scores: scores,
      player_ids: ids,
      player_hits: playersHits,
      time_played: Math.floor(dateEnd - dateStart),
      tournament_type: '2P',
    });
  }, 5000);
}

onMounted(async () => {
  await loadFont();
  setupScene()
  window.addEventListener('resize', () => {
    three.resize(window.innerWidth, window.innerHeight);
  });
  window.addEventListener('keydown', toggleAnimation);
  three.startAnimation(update)
});

onBeforeUnmount(() => {
  three.stopAnimation()
  three.dispose()
  player?.dispose()
  player2?.dispose()
  ball.dispose()
  horizWallDown.dispose()
  horizWallUp.dispose()
  wallMid.dispose()
  scorePlayer1.dispose()
  scorePlayer2.dispose()
  helpTextPlayerOne.dispose()
  helpTextPlayerTwo.dispose()
})
</script>

<template>
  <div></div>
</template>
