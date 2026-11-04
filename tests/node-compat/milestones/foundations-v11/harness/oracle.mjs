import { Buffer } from 'node:buffer';

// Pure xorshift corpus: no ambient clock or entropy enters the component.
export function makeOracleCorpus() {
  let state = 0x57415349;
  const random = () => { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return state >>> 0; };
  const strings = [];
  const bytes = [];
  function string(input, encoding) {
    const expected = Buffer.from(input, encoding);
    strings.push({ input, encoding, bytes: [...expected], text: expected.toString(encoding), byteLength: Buffer.byteLength(input, encoding) });
  }
  for (const [input, encoding] of [['hello', 'utf8'], ['é😀', 'UTF-8'], ['\ufeffBOM', 'utf8'], ['\ud800', 'utf8'],
    ['0001ff', 'hex'], ['AbCd', 'HEX'], ['a', 'hex'], ['12x4', 'hex'], ['12é4', 'hex'], ['12\0a', 'hex'], ['', 'hex']]) string(input, encoding);
  // Put every troublesome UTF-16 character in each position of a hex pair,
  // after valid prefixes of both parities. Later valid pairs must stay unread.
  for (const prefix of ['', '1', '12', '123', '1234']) {
    for (const invalid of ['x', '\0', 'é', '\u0100', '\ud800', '\udfff', '😀', '\uffff']) {
      for (const middle of ['', 'a']) string(prefix + middle + invalid + 'beef', 'hex');
    }
  }
  const alphabet = '0123456789abcdefABCDEF';
  for (let i = 0; i < 220; i++) {
    const length = random() % 257;
    let text = '';
    for (let j = 0; j < length; j++) text += alphabet[random() % alphabet.length];
    if ((i & 3) === 0) {
      const position = random() % (text.length + 1);
      text = text.slice(0, position) + ['x', '\0', '\ud800', 'é'][random() % 4] + text.slice(position);
    }
    string(text, i & 1 ? 'HEX' : 'hex');
  }
  for (let i = 0; i < 70; i++) {
    let text = '';
    for (let j = 0, count = random() % 80; j < count; j++) text += String.fromCharCode(random() & 0xffff);
    string(text, 'utf8');
  }
  for (let i = 0; i < 250; i++) {
    const value = Array.from({ length: i < 8 ? i : random() % 513 }, () => random() & 255);
    const expected = Buffer.from(value);
    bytes.push({ value, hex: expected.toString('hex'), text: expected.toString('utf8') });
  }
  return { seed: '0x57415349', strings, bytes };
}
