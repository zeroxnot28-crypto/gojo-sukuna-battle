from pathlib import Path

p = Path("main.js")
s = p.read_text()

old = '''function updateCombat(dt) {
  attackCooldown = Math.max(0, attackCooldown - dt);
  enemyAttackCooldown = Math.max(0, enemyAttackCooldown - dt);

  const dx = player.position.x - enemy.position.x;
  const dz = player.position.z - enemy.position.z;
  const distance = Math.hypot(dx, dz);

  // Enemy follows the player
  if (distance > 1.4 && enemyHealth > 0 && playerHealth > 0) {
    const speed = 1.8 * dt;
    enemy.position.x += (dx / distance) * speed;
    enemy.position.z += (dz / distance) * speed;
  }

  // Enemy faces the player
  if (distance > 0.01) {
    enemy.rotation.y = Math.atan2(dx, dz);
  }

  // Player attacks by moving close and tapping the attack button
  if (
    attackPressed &&
    attackCooldown <= 0 &&
    distance < 3 &&
    enemyHealth > 0 &&
    playerHealth > 0
  ) {
    enemyHealth = Math.max(0, enemyHealth - 20);
    attackCooldown = 0.5;
  }

  // Enemy damages the player when close
  if (
    distance < 1.5 &&
    enemyAttackCooldown <= 0 &&
    enemyHealth > 0 &&
    playerHealth > 0
  ) {
    playerHealth = Math.max(0, playerHealth - 10);
    enemyAttackCooldown = 1;
  }

  if (enemyHealth <= 0) {
    enemy.visible = false;
    hud.innerHTML = '🏆 YOU WIN!';
  } else if (playerHealth <= 0) {
    hud.innerHTML = '💀 GAME OVER!';
  } else {
    updateHUD();
  }
}'''

new = '''const blueTeam = [{ mesh: player, health: 100, cooldown: 0, human: true }];
const redTeam = [{ mesh: enemy, health: 100, cooldown: 0, human: false }];
let roundOver = false;
let roundNumber = 1;

function addFighter(team, x, z, isBlue) {
  const mesh = isBlue
    ? makeCharacter(0x151b2a, 0xf0c6ad, "gojo")
    : makeCharacter(0x70152b, 0xd9a17f, "sukuna");
  mesh.position.set(x, 0.9, z);
  scene.add(mesh);
  const fighter = { mesh, health: 100, cooldown: 0, human: false };
  team.push(fighter);
}

addFighter(blueTeam, -3, 2, true);
addFighter(blueTeam, -5, 4, true);
addFighter(blueTeam, 2, 5, true);
addFighter(redTeam, 5, -4, false);
addFighter(redTeam, -2, -6, false);
addFighter(redTeam, 6, -7, false);

function updateHUD() {
  const blueAlive = blueTeam.filter(f => f.health > 0).length;
  const redAlive = redTeam.filter(f => f.health > 0).length;
  hud.innerHTML = `
    <div style="color:#82b1ff">🔵 GOJO TEAM: ${blueAlive}/4</div>
    <div style="margin-top:6px">YOU: ${Math.max(0, playerHealth)} HP</div>
    <div style="color:#ff8a80;margin-top:8px">🔴 SUKUNA TEAM: ${redAlive}/4</div>
    <div style="margin-top:8px">Round ${roundNumber}</div>
    <div style="font-size:11px;margin-top:6px">Move close and tap ATTACK</div>
  `;
}

function updateCombat(dt) {
  if (roundOver) return;

  for (const f of blueTeam) {
    if (f.human) f.health = playerHealth;
  }
  for (const f of redTeam) {
    if (f.mesh === enemy) f.health = enemyHealth;
  }

  const all = [
    ...blueTeam.map(f => ({ ...f, team: blueTeam, foes: redTeam })),
    ...redTeam.map(f => ({ ...f, team: redTeam, foes: blueTeam }))
  ];

  for (const f of all) {
    const original = f.team.find(item => item.mesh === f.mesh);
    if (!original || original.health <= 0) {
      f.mesh.visible = false;
      continue;
    }
    original.cooldown = Math.max(0, original.cooldown - dt);

    let target = null;
    let best = Infinity;
    for (const foe of f.foes) {
      if (foe.health <= 0) continue;
      const d = f.mesh.position.distanceTo(foe.mesh.position);
      if (d < best) { best = d; target = foe; }
    }
    if (!target) continue;

    const dx = target.mesh.position.x - f.mesh.position.x;
    const dz = target.mesh.position.z - f.mesh.position.z;
    const distance = Math.hypot(dx, dz);
    f.mesh.rotation.y = Math.atan2(dx, dz);

    if (f.human) {
      if (attackPressed && original.cooldown <= 0 && distance < 3) {
        target.health = Math.max(0, target.health - 20);
        if (target.mesh === enemy) enemyHealth = target.health;
        original.cooldown = 0.5;
      }
    } else if (distance > 1.4) {
      const speed = f.team === blueTeam ? 1.5 : 1.8;
      f.mesh.position.x += dx / Math.max(distance, 0.01) * speed * dt;
      f.mesh.position.z += dz / Math.max(distance, 0.01) * speed * dt;
    } else if (original.cooldown <= 0) {
      target.health = Math.max(0, target.health - 8);
      if (target.mesh === player) playerHealth = target.health;
      if (target.mesh === enemy) enemyHealth = target.health;
      original.cooldown = 0.9;
    }
  }

  const blueAlive = blueTeam.filter(f => f.health > 0).length;
  const redAlive = redTeam.filter(f => f.health > 0).length;

  for (const f of [...blueTeam, ...redTeam]) {
    f.mesh.visible = f.health > 0;
  }

  if (blueAlive === 0 || redAlive === 0) {
    roundOver = true;
    hud.innerHTML = blueAlive > 0
      ? `🏆 GOJO TEAM WINS ROUND ${roundNumber}!`
      : `💀 SUKUNA TEAM WINS ROUND ${roundNumber}!`;
    return;
  }
  updateHUD();
}'''

if old not in s:
    print("ERROR: Original combat block not found. No changes made.")
    raise SystemExit(1)

s = s.replace(old, new, 1)
s = s.replace("  const dt = Math.min(clock.getDelta(), 0.05);", "  const dt = Math.min(clock.getDelta(), 0.05);\\n  updateCombat(dt);", 1)
p.write_text(s)
print("SUCCESS: 4v4 battle system added.")
print("Backup: main.js.before-4v4-system")
