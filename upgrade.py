from pathlib import Path

p = Path("main.js")
s = p.read_text()

start = s.find("function makeCharacter(color, skinColor) {")
end_marker = "const held = new Set();"
end = s.find(end_marker, start)

if start < 0 or end < 0:
    print("ERROR: Character section not found. No changes made.")
    raise SystemExit(1)

character_code = r'''
function makeCharacter(color, skinColor, type = "gojo") {
  const character = new THREE.Group();
  const outfit = new THREE.MeshStandardMaterial({ color, roughness: 0.8 });
  const skin = new THREE.MeshStandardMaterial({ color: skinColor });
  const dark = new THREE.MeshStandardMaterial({ color: 0x171923 });
  const hairColor = type === "gojo" ? 0xf5f5ff : 0xf08b9c;
  const hair = new THREE.MeshStandardMaterial({ color: hairColor });
  const red = new THREE.MeshStandardMaterial({ color: 0x9e142b });
  const black = new THREE.MeshStandardMaterial({ color: 0x19151c });

  function part(geometry, material, x, y, z) {
    const m = new THREE.Mesh(geometry, material);
    m.position.set(x, y, z);
    m.castShadow = true;
    character.add(m);
    return m;
  }

  // Body and legs
  part(new THREE.CapsuleGeometry(0.32, 0.5, 4, 8), outfit, 0, 0.12, 0);
  part(new THREE.CapsuleGeometry(0.14, 0.45, 3, 6), outfit, -0.18, -0.48, 0);
  part(new THREE.CapsuleGeometry(0.14, 0.45, 3, 6), outfit, 0.18, -0.48, 0);
  part(new THREE.BoxGeometry(0.28, 0.13, 0.38), dark, -0.18, -0.76, -0.04);
  part(new THREE.BoxGeometry(0.28, 0.13, 0.38), dark, 0.18, -0.76, -0.04);

  // Arms
  part(new THREE.CapsuleGeometry(0.1, 0.43, 3, 6), outfit, -0.4, 0.12, 0);
  part(new THREE.CapsuleGeometry(0.1, 0.43, 3, 6), outfit, 0.4, 0.12, 0);
  part(new THREE.SphereGeometry(0.11, 8, 6), skin, -0.41, -0.17, 0);
  part(new THREE.SphereGeometry(0.11, 8, 6), skin, 0.41, -0.17, 0);

  // Neck and face
  part(new THREE.CylinderGeometry(0.1, 0.12, 0.17, 8), skin, 0, 0.48, 0);
  part(new THREE.SphereGeometry(0.235, 12, 10), skin, 0, 0.77, 0);

  if (type === "gojo") {
    // Dark blindfold and spiky white hair
    part(new THREE.BoxGeometry(0.39, 0.105, 0.09), dark, 0, 0.8, -0.205);
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * Math.PI * 2;
      const spike = part(
        new THREE.ConeGeometry(0.085, 0.27 + (i % 3) * 0.035, 5),
        hair,
        Math.cos(a) * 0.16,
        0.99 + (i % 2) * 0.025,
        Math.sin(a) * 0.12
      );
      spike.rotation.z = Math.cos(a) * -0.5;
      spike.rotation.x = Math.sin(a) * 0.45;
    }
  } else {
    // Sukuna-inspired pink hair and facial markings
    part(new THREE.SphereGeometry(0.25, 10, 7), hair, 0, 0.91, 0);
    part(new THREE.BoxGeometry(0.32, 0.025, 0.025), red, 0, 0.79, -0.22);
    part(new THREE.BoxGeometry(0.025, 0.13, 0.025), red, -0.09, 0.72, -0.22);
    part(new THREE.BoxGeometry(0.025, 0.13, 0.025), red, 0.09, 0.72, -0.22);
    part(new THREE.ConeGeometry(0.09, 0.18, 5), hair, -0.16, 1.02, 0);
    part(new THREE.ConeGeometry(0.09, 0.18, 5), hair, 0.16, 1.02, 0);
  }

  return character;
}

const player = makeCharacter(0x151b2a, 0xf0c6ad, "gojo");
player.position.set(0, 0.9, 3);
scene.add(player);

const enemy = makeCharacter(0x70152b, 0xd9a17f, "sukuna");
enemy.position.set(3, 0.9, -3);
scene.add(enemy);
'''

s = s[:start] + character_code + s[end:]
p.write_text(s)
print("SUCCESS: Character upgrade applied.")
print("Backup available: main.js.before-4v4")
