'use strict'

const { ArrayPrototypePop, Promise } = require("lib/ours/primordials.js")
const { isIterable, isNodeStream, isWebStream } = require("lib/internal/streams/utils.js")
const { pipelineImpl: pl } = require("lib/internal/streams/pipeline.js")
const { finished } = require("lib/internal/streams/end-of-stream.js")
require("lib/stream.js")
function pipeline(...streams) {
  return new Promise((resolve, reject) => {
    let signal
    let end
    const lastArg = streams[streams.length - 1]
    if (
      lastArg &&
      typeof lastArg === 'object' &&
      !isNodeStream(lastArg) &&
      !isIterable(lastArg) &&
      !isWebStream(lastArg)
    ) {
      const options = ArrayPrototypePop(streams)
      signal = options.signal
      end = options.end
    }
    pl(
      streams,
      (err, value) => {
        if (err) {
          reject(err)
        } else {
          resolve(value)
        }
      },
      {
        signal,
        end
      }
    )
  })
}
module.exports = {
  finished,
  pipeline
}
