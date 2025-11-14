/*
 * Functions for 2D transformations (column-major for WebGL)
 *
 * Gilberto Echeverria
 * 2024-11-04
 */

class V2 {
    static create(px, py) {
        const v = new Float32Array(2);
        v[0] = px;
        v[1] = py;
        return v;
    }
}

class M3 {
    static identity() {
        return [
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        ];
    }

    static scale(vs) {
        const sx = vs[0];
        const sy = vs[1];
        return [
            sx, 0,  0,
            0,  sy, 0,
            0,  0,  1
        ];
    }

    static translation(vt) {
        const tx = vt[0];
        const ty = vt[1];
        return [
            1, 0, 0,
            0, 1, 0,
            tx, ty, 1
        ];
    }

    static rotation(angleRadians) {
        const c = Math.cos(angleRadians);
        const s = Math.sin(angleRadians);
        return [
            c,  s, 0,
           -s,  c, 0,
            0,  0, 1
        ];
    }

    static multiply(a, b) {
        const a00 = a[0], a01 = a[1], a02 = a[2];
        const a10 = a[3], a11 = a[4], a12 = a[5];
        const a20 = a[6], a21 = a[7], a22 = a[8];

        const b00 = b[0], b01 = b[1], b02 = b[2];
        const b10 = b[3], b11 = b[4], b12 = b[5];
        const b20 = b[6], b21 = b[7], b22 = b[8];

        return [
            
            a00 * b00 + a10 * b01 + a20 * b02,
            a01 * b00 + a11 * b01 + a21 * b02,
            a02 * b00 + a12 * b01 + a22 * b02,

            
            a00 * b10 + a10 * b11 + a20 * b12,
            a01 * b10 + a11 * b11 + a21 * b12,
            a02 * b10 + a12 * b11 + a22 * b12,

            
            a00 * b20 + a10 * b21 + a20 * b22,
            a01 * b20 + a11 * b21 + a21 * b22,
            a02 * b20 + a12 * b21 + a22 * b22,
        ];
    }
}

export { V2, M3 };
