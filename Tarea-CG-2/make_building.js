/*
 * Generates an OBJ file for a building with a specified number of sides, height,
 * and radius for the bottom and top.
 *
 * Paolo Zesati Negrete
 * 2025-11-24
 */


const fs = require("fs");

const args = process.argv.slice(2);

const numSides = parseInt(args[0]) || 8;
const height = parseFloat(args[1]) || 6.0;
const bottomRadius = parseFloat(args[2]) || 1.0;
const topRadius = parseFloat(args[3]) || 0.8;

if (numSides < 3 || numSides > 36) {
    console.error("El número de lados debe estar entre 3 y 36.");
    process.exit(1);
}

function normalize(v) {
    const len = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
    return [v[0]/len, v[1]/len, v[2]/len];
}

function cross(a, b) {
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ];
}

function computeNormal(a, b, c) {
    const u = [b[0]-a[0], b[1]-a[1], b[2]-a[2]];
    const v = [c[0]-a[0], c[1]-a[1], c[2]-a[2]];
    return normalize(cross(u, v));
}

function generarOBJ() {
    let vertices = [];
    let normals = [];
    let faces = [];

    for (let i = 0; i < numSides; i++) {
        const ang = i * 2 * Math.PI / numSides;
        vertices.push([
            Math.cos(ang) * bottomRadius,
            0,
            Math.sin(ang) * bottomRadius
        ]);
    }

    for (let i = 0; i < numSides; i++) {
        const ang = i * 2 * Math.PI / numSides;
        vertices.push([
            Math.cos(ang) * topRadius,
            height,
            Math.sin(ang) * topRadius
        ]);
    }

    const bottomCenterIndex = vertices.length;
    vertices.push([0, 0, 0]);

    const topCenterIndex = vertices.length;
    vertices.push([0, height, 0]);

    normals.push([0, -1, 0]);
    normals.push([0, 1, 0]);

    for (let i = 0; i < numSides; i++) {
        const next = (i + 1) % numSides;
        const n = computeNormal(
            vertices[i],
            vertices[next],
            vertices[i + numSides]
        );
        normals.push(n);
        normals.push(n);
    }

    const baseN = 3;

    for (let i = 0; i < numSides; i++) {
        const next = (i + 1) % numSides;

        const b1 = i + 1;
        const b2 = next + 1;
        const t1 = i + 1 + numSides;
        const t2 = next + 1 + numSides;

        const nIdx = baseN + i*2;

        faces.push([b1, b2, t1, nIdx]);
        faces.push([b2, t2, t1, nIdx + 1]);
    }

    for (let i = 0; i < numSides; i++) {
        const next = (i + 1) % numSides;
        faces.push([
            bottomCenterIndex + 1,
            next + 1,
            i + 1,
            1
        ]);
    }

    for (let i = 0; i < numSides; i++) {
        const next = (i + 1) % numSides;
        faces.push([
            topCenterIndex + 1,
            i + 1 + numSides,
            next + 1 + numSides,
            2
        ]);
    }

    let out = "";

    out += `# OBJ file\n`;
    out += `# ${vertices.length} vertices\n`;

    vertices.forEach(v => {
        out += `v ${v[0].toFixed(4)} ${v[1].toFixed(4)} ${v[2].toFixed(4)}\n`;
    });

    out += `# ${normals.length} normals\n`;

    normals.forEach(n => {
        out += `vn ${n[0].toFixed(4)} ${n[1].toFixed(4)} ${n[2].toFixed(4)}\n`;
    });

    out += `# ${faces.length} faces\n`;

    faces.forEach(f => {
        out += `f ${f[0]}//${f[3]} ${f[1]}//${f[3]} ${f[2]}//${f[3]}\n`;
    });

    return out;
}

const output = generarOBJ();
const filename = `building_${numSides}_${height}_${bottomRadius}_${topRadius}.obj`;
fs.writeFileSync(filename, output);
console.log(`Archivo OBJ generado: ${filename}`);
