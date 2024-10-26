import { Vector3, Color } from 'three';

export const dateStart = Date.now() / 1000;

// Define bounds of the Pong game
export const bounds = { minX: -16.2, maxX: 16.2, minY: -9.2, maxY: 9.2, minZ: 0, maxZ: 0 };

// Ball and walls
const ballVectorY = Math.random() * 0.2 - 0.1;

let ballVelocityX = -0.25;
export let ballVelocity = new Vector3(ballVelocityX, ballVectorY, 0);;

export function setBallVelocity (aiDiff: number) {	
	switch (aiDiff) {
	  case 0.3:
		ballVelocityX = -0.15;
		break ;
	  case 0.5:
		ballVelocityX = -0.20;
		break ;
	  case 1:
		ballVelocityX = -0.25;
		break ;
	  case 1.5:
		ballVelocityX = -0.30;
		break ;
	  default:
		ballVelocityX = -0.25;
		break ;
	}
	console.log('AI Speed: ', ballVelocityX);
	ballVelocity = new Vector3(ballVelocityX, ballVectorY, 0);
}

export const ballGeometry = [0.33, 10, 10];

export const ballGeometry2 = [0.66, 10, 10];

export const vecHorizWall = new Vector3(33, 0.3, 1);

export const BIT_FONT = './src/assets/fonts/Bit5x3_Regular.json';
export const MONTSERRAT_FONT = './src/assets/fonts/Montserrat.json';