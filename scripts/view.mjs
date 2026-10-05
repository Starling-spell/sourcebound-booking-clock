import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import dns from 'node:dns';
dns.setDefaultResultOrder('ipv4first');
const [address, functionName, rawArgs = '[]'] = process.argv.slice(2);
if (!/^0x[0-9a-fA-F]{40}$/.test(address ?? '') || !functionName) throw Error('Address and view method required');
const args = JSON.parse(rawArgs);
if (!Array.isArray(args)) throw Error('JSON argument array required');
const client = createClient({chain: studionet});
console.log(JSON.stringify(await client.readContract({address, functionName, args}), (_, value) =>
  typeof value === 'bigint' ? value.toString() : value));
