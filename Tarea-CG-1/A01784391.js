'use strict';

import * as twgl from 'twgl';
import { shapeSmiley, shapeLeftEye, shapeRightEye, shapeMouth, pivotSquare } from './shapes.js';
import { M3 } from './A01784391-2d-libs.js';
import GUI from 'lil-gui';

// ===== SHADERS =====
const vsGLSL = `#version 300 es
in vec2 a_position;
uniform vec2 u_resolution;
uniform mat3 u_transforms;

void main() {
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;
    vec2 zeroToOne = position / u_resolution;
    vec2 zeroToTwo = zeroToOne * 2.0;
    vec2 clipSpace = zeroToTwo - 1.0;
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

const fsGLSL = `#version 300 es
precision highp float;
uniform vec4 u_color;
out vec4 outColor;
void main() {
    outColor = u_color;
}
`;

const objects = {
    face: {
        shape: shapeSmiley(),
        color: [1, 0.85, 0, 1],
        transform: { x: 120, y: 0, scale: 1, rot: 0 }
    },
    leftEye: {
        shape: shapeLeftEye(),
        color: [0, 0, 0, 1],
        offset: [-30, -50]
    },
    rightEye: {
        shape: shapeRightEye(),
        color: [0, 0, 0, 1],
        offset: [30, -50]
    },
    mouth: {
        shape: shapeMouth(),
        color: [1, 1, 1, 1],
        offset: [0, 40]
    },
    pivot: {
        shape: pivotSquare(),
        color: [1, 0, 0, 1],
        transform: { x: 400, y: 250 }  
    }
};


function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    
    for (let key in objects) {
        const obj = objects[key];
        obj.bufferInfo = twgl.createBufferInfoFromArrays(gl, obj.shape);
        obj.vao = twgl.createVAOFromBufferInfo(gl, programInfo, obj.bufferInfo);
    }

    setupUI(gl);
    drawScene(gl, programInfo);
}

function drawScene(gl, programInfo) {
    gl.clearColor(1, 1, 1, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    
    const face = objects.face;
    const pivot = objects.pivot;

    let faceMat = M3.identity();
    faceMat = M3.translation([-pivot.transform.x, -pivot.transform.y]);
    faceMat = M3.multiply(M3.rotation(face.transform.rot),faceMat);
    faceMat = M3.multiply(M3.translation([pivot.transform.x, pivot.transform.y]),faceMat);
    faceMat = M3.multiply(M3.scale([face.transform.scale, face.transform.scale]),faceMat);
    faceMat = M3.multiply(M3.translation([face.transform.x, face.transform.y]),faceMat);


    drawShape(gl, programInfo, face, faceMat);

    
    const mouth = objects.mouth;
    const mouthMat = M3.multiply(faceMat, M3.translation(mouth.offset));
    drawShape(gl, programInfo, mouth, mouthMat);

    
    const leftEye = objects.leftEye;
    const rightEye = objects.rightEye;
    const leftMat = M3.multiply(faceMat, M3.translation(leftEye.offset));
    const rightMat = M3.multiply(faceMat, M3.translation(rightEye.offset));
    drawShape(gl, programInfo, leftEye, leftMat);
    drawShape(gl, programInfo, rightEye, rightMat);


    const pivotMat = M3.translation([pivot.transform.x, pivot.transform.y]);
    drawShape(gl, programInfo, pivot, pivotMat);

    requestAnimationFrame(() => drawScene(gl, programInfo));
}

function drawShape(gl, programInfo, obj, transform) {
    gl.useProgram(programInfo.program);
    gl.bindVertexArray(obj.vao);

    const uniforms = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transform,
        u_color: obj.color,
    };

    twgl.setUniforms(programInfo, uniforms);
    twgl.drawBufferInfo(gl, obj.bufferInfo);
}

function setupUI(gl) {
    const gui = new GUI();
    const pivotFolder = gui.addFolder('Pivot');
    const faceFolder = gui.addFolder('Face');

    pivotFolder.add(objects.pivot.transform, 'x', 0, gl.canvas.width);
    pivotFolder.add(objects.pivot.transform, 'y', 0, gl.canvas.height);

    faceFolder.add(objects.face.transform, 'x', 0,gl.canvas.width);
    faceFolder.add(objects.face.transform, 'y', 0,gl.canvas.height);
    faceFolder.add(objects.face.transform, 'rot', 0, Math.PI * 2);
    faceFolder.add(objects.face.transform, 'scale', 0.5, 2);
}

main();
