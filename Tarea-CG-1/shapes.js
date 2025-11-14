/*
 * Shapes for the Smiley Face
 *
 * Paolo Zesati Negrete
 * 2025-11-13
 */

'use strict';


export function shapeSmiley() {
    const arrays = {
        a_position: {
            numComponents: 2,
            data: [
                0, 0,
                0, 100,
                70, 70,
                100, 0,
                70, -70,
                0, -100,
                -70, -70,
                -100, 0,
                -70, 70,
                0, 100  
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 2,
                0, 2, 3,
                0, 3, 4,
                0, 4, 5,
                0, 5, 6,
                0, 6, 7,
                0, 7, 8,
                0, 8, 9
            ]
        }
    };
    return arrays;
}

export function shapeLeftEye() {
    const arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -10, -10,
                10, -10,
                0, 10
            ]
        },
        indices: {
            numComponents: 3,
            data: [0, 1, 2]
        }
    };
    return arrays;
}

export function shapeRightEye() {
    const arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -10, -10,
                10, -10,
                0, 10
            ]
        },
        indices: {
            numComponents: 3,
            data: [0, 1, 2]
        }
    };
    return arrays;
}

// ---------- MOUTH ----------
export function shapeMouth() {
    const arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -30, -10,
                30, -10,
                0, 10
            ]
        },
        indices: {
            numComponents: 3,
            data: [0, 1, 2]
        }
    };
    return arrays; 
}

export function pivotSquare() {
    const arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -5, -5,
                5, -5,
                5, 5,
                -5, 5
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 2,
                2, 3, 0
            ]
        }
    };
    return arrays;
}
