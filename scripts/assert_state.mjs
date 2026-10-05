import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import dns from 'node:dns';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
dns.setDefaultResultOrder('ipv4first');
const address = process.argv[2];
if (!/^0x[0-9a-fA-F]{40}$/.test(address ?? '')) throw Error('Demo contract address required');
const client = createClient({chain: studionet});
const read = (functionName, args) => client.readContract({address, functionName, args});
const [calendar, occupancy, reservation, uncertain, unavailable, history] = await Promise.all([
  read('get_calendar', ['observatory']), read('get_occupancy', ['observatory']),
  read('get_reservation', ['observatory', 'booking1']), read('get_calendar', ['uncertain']),
  read('get_calendar', ['wronghash']), read('history', [0, 20])]);
const canonical = value => JSON.stringify(value, function(key, item) {
  return item && typeof item === 'object' && !Array.isArray(item)
    ? Object.fromEntries(Object.keys(item).sort().map(k => [k, item[k]])) : item;
});
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
assert.equal(calendar.state, 'READY');
assert.equal(calendar.http, 200);
assert.equal(sha(calendar.text), calendar.spec.expected_hash);
assert.equal(calendar.hash, calendar.spec.expected_hash);
const expectedDays = [[[18,24],[26,34]], [[18,24],[26,34]], [[20,28]], [[18,24],[26,34]], [[18,24],[26,34]], [[20,24]], []];
const expected = expectedDays.map(intervals => Array.from({length:48}, (_, slot) =>
  intervals.some(([start,end]) => start <= slot && slot < end) ? '1' : '0').join('')).join('');
assert.equal(calendar.mask, expected);
assert.equal(calendar.root, sha(canonical(Object.fromEntries(Object.entries(calendar).filter(([key]) => key !== 'root')))));
assert.equal(occupancy, '0'.repeat(336));
assert.equal(reservation.state, 'CANCELLED');
assert.equal(reservation.calendar, 'observatory');
assert.equal(reservation.first, 18);
assert.equal(reservation.count, 2);
assert.equal(reservation.evidence_root, calendar.root);
assert.equal(reservation.principal, calendar.spec.owner);
assert.equal(uncertain.state, 'AMBIGUOUS');
assert.equal(uncertain.mask, '');
assert.equal(sha(uncertain.text), uncertain.spec.expected_hash);
assert.equal(unavailable.state, 'UNAVAILABLE');
assert.equal(unavailable.mask, '');
assert.notEqual(unavailable.hash, unavailable.spec.expected_hash);
assert.deepEqual(history.map(item => item.operation), ['CALENDAR','RESERVE','CANCEL','CALENDAR','CALENDAR']);
for (let i = 0; i < history.length; i++) {
  assert.equal(history[i].previous, i ? history[i-1].root : '');
  assert.equal(history[i].root, sha(canonical(Object.fromEntries(Object.entries(history[i]).filter(([key]) => key !== 'root')))));
}
assert.equal(history[1].reservation.state, 'RESERVED');
assert.equal(history[2].reservation.state, 'CANCELLED');
console.log(JSON.stringify({assertions:'PASS', calendar_state:calendar.state, open_slots:68,
  occupied_slots:0, booking_state:reservation.state, ambiguous_state:uncertain.state,
  wronghash_state:unavailable.state, events:history.length, evidence_root:calendar.root,
  journal_root:history.at(-1).root}));
