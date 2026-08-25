/**
 * SOPHIE-X — Physical Modeling & Hyperpop Latex Sound Engine
 * Inspired by SOPHIE (BIPP, Faceshopping, Lemonade, Immaterial, Ponyboy, MSMSMSM).
 * Features: Liquid Bubble Pops, Elastic Latex Plucks, Inharmonic Metallic Clangs,
 * Monomachine Distorted Tanh Bass, Formant Vocal Resonators, and Real-time Liquid Membrane Vector Scope.
 */

(function (window, document) {
  'use strict';

  // --- Note Frequency Map ---
  var NOTE_FREQ = {
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
    'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
    'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
    'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99
  };

  var KEY_NOTE_MAP = {
    'a': 'C4', 'w': 'C#4', 's': 'D4', 'e': 'D#4', 'd': 'E4',
    'f': 'F4', 't': 'F#4', 'g': 'G4', 'y': 'G#4', 'h': 'A4',
    'u': 'A#4', 'j': 'B4', 'k': 'C5', 'o': 'C#5', 'l': 'D5'
  };

  // --- SOPHIE Signature Physical Modeling Sound Presets ---
  var PRESETS = {
    'bipp_bubble': {
      name: '✦ 01: BIPP BUBBLE POP (Liquid Rubber)',
      oscType: 'sine',
      elasticity: 0.95,
      pitchSnap: 0.85,
      metallicFM: 0.1,
      filterCutoff: 3200,
      filterRes: 18.0,
      formant: 'u',
      drive: 0.2,
      reverb: 0.35,
      attack: 0.001,
      decay: 0.18,
      sustain: 0.0,
      release: 0.15
    },
    'faceshopping_bass': {
      name: '✦ 02: FACESHOPPING BASS (Abrasive Metal Tanh)',
      oscType: 'sawtooth',
      elasticity: 0.4,
      pitchSnap: 0.3,
      metallicFM: 0.65,
      filterCutoff: 950,
      filterRes: 12.0,
      formant: 'none',
      drive: 0.95,
      reverb: 0.15,
      attack: 0.01,
      decay: 0.45,
      sustain: 0.85,
      release: 0.25
    },
    'lemonade_clang': {
      name: '✦ 03: LEMONADE CLANG (Inharmonic FM Metal)',
      oscType: 'triangle',
      elasticity: 0.8,
      pitchSnap: 0.9,
      metallicFM: 0.95,
      filterCutoff: 5500,
      filterRes: 22.0,
      formant: 'i',
      drive: 0.8,
      reverb: 0.5,
      attack: 0.002,
      decay: 0.35,
      sustain: 0.1,
      release: 0.4
    },
    'immaterial_lead': {
      name: '✦ 04: IMMATERIAL SHIMMER (Euphoric Hyperpop)',
      oscType: 'square',
      elasticity: 0.5,
      pitchSnap: 0.2,
      metallicFM: 0.25,
      filterCutoff: 4200,
      filterRes: 6.0,
      formant: 'a',
      drive: 0.3,
      reverb: 0.8,
      attack: 0.04,
      decay: 0.5,
      sustain: 0.7,
      release: 1.2
    },
    'ponyboy_whip': {
      name: '✦ 05: PONYBOY WHIP (Latex Elastic Strike)',
      oscType: 'sawtooth',
      elasticity: 1.0,
      pitchSnap: 1.0,
      metallicFM: 0.8,
      filterCutoff: 2400,
      filterRes: 16.0,
      formant: 'o',
      drive: 0.85,
      reverb: 0.2,
      attack: 0.001,
      decay: 0.12,
      sustain: 0.0,
      release: 0.1
    }
  };

  // --- Synth State & DSP Graph ---
  var synth = {
    ctx: null,
    masterGain: null,
    analyser: null,
    filterNode: null,
    waveshaper: null,
    reverbNode: null,
    activeVoices: {},
    params: Object.assign({}, PRESETS['bipp_bubble']),
    sequencer: {
      bpm: 135, // High-energy SOPHIE hyperpop tempo
      isPlaying: false,
      currentStep: 0,
      timerId: null,
      steps: [true, false, true, true, false, true, false, true, true, false, true, false, true, true, false, true],
      notes: ['C4', 'C5', 'D#4', 'G4', 'C4', 'A#4', 'G4', 'D#5', 'C4', 'C5', 'F#4', 'G4', 'C5', 'D#5', 'G5', 'C5']
    },
    recorder: {
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      destNode: null
    }
  };

  function initAudio() {
    if (synth.ctx) return;
    var AudioContext = window.AudioContext || window.webkitAudioContext;
    synth.ctx = new AudioContext();

    synth.masterGain = synth.ctx.createGain();
    synth.masterGain.gain.setValueAtTime(0.55, synth.ctx.currentTime);

    synth.analyser = synth.ctx.createAnalyser();
    synth.analyser.fftSize = 1024;

    synth.waveshaper = synth.ctx.createWaveShaper();
    updateDistortionCurve(synth.params.drive);

    synth.filterNode = synth.ctx.createBiquadFilter();
    synth.filterNode.type = 'lowpass';
    synth.filterNode.frequency.setValueAtTime(synth.params.filterCutoff, synth.ctx.currentTime);
    synth.filterNode.Q.setValueAtTime(synth.params.filterRes, synth.ctx.currentTime);

    synth.reverbNode = synth.ctx.createConvolver();
    synth.reverbNode.buffer = createReverbImpulse(synth.ctx, 2.0, 2.5);

    var reverbGain = synth.ctx.createGain();
    reverbGain.gain.setValueAtTime(synth.params.reverb, synth.ctx.currentTime);

    var dryGain = synth.ctx.createGain();
    dryGain.gain.setValueAtTime(1.0 - synth.params.reverb * 0.4, synth.ctx.currentTime);

    synth.waveshaper.connect(dryGain);
    synth.waveshaper.connect(synth.reverbNode);
    synth.reverbNode.connect(reverbGain);

    dryGain.connect(synth.masterGain);
    reverbGain.connect(synth.masterGain);

    synth.masterGain.connect(synth.analyser);
    synth.analyser.connect(synth.ctx.destination);

    synth.recorder.destNode = synth.ctx.createMediaStreamDestination();
    synth.masterGain.connect(synth.recorder.destNode);
  }

  // --- Monomachine Style Extreme Tanh Waveshaping ---
  function updateDistortionCurve(k) {
    if (!synth.waveshaper) return;
    var n = 512;
    var curve = new Float32Array(n);
    var amount = k * 65.0;
    for (var i = 0; i < n; ++i) {
      var x = (i * 2) / n - 1;
      // Hyperbolic tangent with asymmetric hard clipping for metallic pop
      curve[i] = Math.tanh(x * (1.0 + amount)) + (k > 0.6 ? Math.sin(x * Math.PI * 4) * 0.15 : 0);
    }
    synth.waveshaper.curve = curve;
  }

  function createReverbImpulse(ctx, duration, decay) {
    var rate = ctx.sampleRate;
    var length = rate * duration;
    var impulse = ctx.createBuffer(2, length, rate);
    var left = impulse.getChannelData(0);
    var right = impulse.getChannelData(1);

    for (var i = 0; i < length; i++) {
      var t = i / length;
      var env = Math.pow(1 - t, decay);
      left[i] = ((Math.random() * 2) - 1) * env;
      right[i] = ((Math.random() * 2) - 1) * env;
    }
    return impulse;
  }

  // --- SOPHIE Physical Modeling Voice Trigger ---
  function triggerNoteOn(noteName) {
    initAudio();
    if (synth.ctx.state === 'suspended') {
      synth.ctx.resume();
    }

    var freq = NOTE_FREQ[noteName];
    if (!freq) return;

    if (synth.activeVoices[noteName]) {
      triggerNoteOff(noteName);
    }

    var now = synth.ctx.currentTime;
    var p = synth.params;

    // 1. Primary Physical Modeling Carrier Oscillator
    var osc1 = synth.ctx.createOscillator();
    osc1.type = p.oscType;

    // Fast Pitch Snap (Liquid Bubble Pop & Latex Stretch)
    if (p.pitchSnap > 0.05) {
      var snapFactor = 1.0 + p.pitchSnap * 3.5;
      osc1.frequency.setValueAtTime(freq * snapFactor, now);
      osc1.frequency.exponentialRampToValueAtTime(freq, now + 0.03 + (1.0 - p.pitchSnap) * 0.08);
    } else {
      osc1.frequency.setValueAtTime(freq, now);
    }

    // 2. Inharmonic FM Modulator (Metallic Lemonade / Sheet Metal Clang)
    var modOsc = null;
    var modGain = null;
    if (p.metallicFM > 0.05) {
      modOsc = synth.ctx.createOscillator();
      modOsc.type = 'sine';
      // Inharmonic FM ratio (Golden ratio / sqrt(2))
      modOsc.frequency.setValueAtTime(freq * 2.414, now);

      modGain = synth.ctx.createGain();
      var fmDepth = freq * p.metallicFM * 4.0;
      modGain.gain.setValueAtTime(fmDepth, now);
      modGain.gain.exponentialRampToValueAtTime(0.01, now + p.decay * 0.8);

      modOsc.connect(modGain);
      modGain.connect(osc1.frequency);
      modOsc.start(now);
    }

    // 3. Elastic Sub Oscillator (-1 Octave)
    var subOsc = synth.ctx.createOscillator();
    subOsc.type = 'sine';
    subOsc.frequency.setValueAtTime(freq * 0.5, now);

    var subGain = synth.ctx.createGain();
    subGain.gain.setValueAtTime(0.75, now);
    subOsc.connect(subGain);

    // Voice Envelope (ADSR)
    var voiceGain = synth.ctx.createGain();
    voiceGain.gain.setValueAtTime(0.0001, now);
    voiceGain.gain.linearRampToValueAtTime(0.45, now + p.attack);
    voiceGain.gain.exponentialRampToValueAtTime(Math.max(0.0001, 0.45 * p.sustain), now + p.attack + p.decay);

    osc1.connect(voiceGain);
    subGain.connect(voiceGain);
    voiceGain.connect(synth.filterNode);
    synth.filterNode.connect(synth.waveshaper);

    osc1.start(now);
    subOsc.start(now);

    synth.activeVoices[noteName] = {
      osc1: osc1,
      modOsc: modOsc,
      subOsc: subOsc,
      gain: voiceGain
    };

    var keyEl = document.querySelector('[data-note="' + noteName + '"]');
    if (keyEl) keyEl.classList.add('pressed');
  }

  function triggerNoteOff(noteName) {
    var voice = synth.activeVoices[noteName];
    if (!voice || !synth.ctx) return;

    var now = synth.ctx.currentTime;
    var p = synth.params;

    voice.gain.gain.cancelScheduledValues(now);
    voice.gain.gain.setValueAtTime(voice.gain.gain.value, now);
    voice.gain.gain.exponentialRampToValueAtTime(0.0001, now + p.release);

    setTimeout(function () {
      try {
        voice.osc1.stop();
        if (voice.modOsc) voice.modOsc.stop();
        voice.subOsc.stop();
        voice.osc1.disconnect();
        voice.subOsc.disconnect();
        voice.gain.disconnect();
      } catch (e) {}
    }, (p.release + 0.1) * 1000);

    delete synth.activeVoices[noteName];

    var keyEl = document.querySelector('[data-note="' + noteName + '"]');
    if (keyEl) keyEl.classList.remove('pressed');
  }

  // =========================================================================
  // SOPHIE LIQUID MEMBRANE & PHOSPHOR VECTOR CRT SCOPE
  // =========================================================================
  function initOscilloscope() {
    var canvas = document.getElementById('crt-scope-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    function resize() {
      var rect = canvas.parentElement.getBoundingClientRect();
      var dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    }
    resize();
    window.addEventListener('resize', resize);

    var timeData = new Uint8Array(512);
    var freqData = new Uint8Array(64);
    var phaseAnim = 0;

    function drawScope() {
      phaseAnim += 0.04;
      var w = canvas.width / (window.devicePixelRatio || 1);
      var h = canvas.height / (window.devicePixelRatio || 1);
      ctx.clearRect(0, 0, w, h);

      var cx = w / 2;
      var cy = h / 2;

      // Dark Latex Vinyl Screen
      ctx.fillStyle = '#08030b';
      ctx.fillRect(0, 0, w, h);

      // Pink Grid Overlay
      ctx.strokeStyle = 'rgba(255, 0, 119, 0.15)';
      ctx.lineWidth = 1;
      for (var x = 0; x < w; x += 30) {
        ctx.beginPath();
        ctx.moveTo(x, 0); ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (var y = 0; y < h; y += 25) {
        ctx.beginPath();
        ctx.moveTo(0, y); ctx.lineTo(w, y);
        ctx.stroke();
      }

      if (synth.analyser) {
        synth.analyser.getByteTimeDomainData(timeData);
        synth.analyser.getByteFrequencyData(freqData);

        // 1. Deforming Liquid Bubble Membrane (Pink Latex Fluid Simulation)
        ctx.beginPath();
        var bubbleRadius = Math.min(w, h) * 0.32;
        var numPoints = 24;
        for (var p = 0; p <= numPoints; p++) {
          var ang = (p / numPoints) * Math.PI * 2;
          var sampleIdx = Math.floor((p / numPoints) * timeData.length);
          var displacement = ((timeData[sampleIdx] - 128) / 128.0) * (bubbleRadius * 0.6);
          var r = bubbleRadius + displacement + Math.sin(phaseAnim * 3 + p * 2) * 6;
          var px = cx + Math.cos(ang) * r;
          var py = cy + Math.sin(ang) * r;
          if (p === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.strokeStyle = '#ff0077';
        ctx.lineWidth = 3;
        ctx.shadowColor = '#ff0077';
        ctx.shadowBlur = 16;
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 0, 119, 0.12)';
        ctx.fill();
        ctx.shadowBlur = 0;

        // 2. Cyan Laser Waveform Trace (High Energy Metallic Cut)
        ctx.beginPath();
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 8;
        var sliceW = w / timeData.length;
        for (var j = 0; j < timeData.length; j++) {
          var val = (timeData[j] - 128) / 128.0;
          var wy = cy + val * (h * 0.4);
          var wx = j * sliceW;
          if (j === 0) ctx.moveTo(wx, wy);
          else ctx.lineTo(wx, wy);
        }
        ctx.stroke();
        ctx.shadowBlur = 0;

        // 3. Yellow Candy Spectrum Bars (Bottom)
        ctx.fillStyle = 'rgba(255, 230, 0, 0.4)';
        var barW = w / freqData.length;
        for (var k = 0; k < freqData.length; k++) {
          var barH = (freqData[k] / 255.0) * (h * 0.28);
          ctx.fillRect(k * barW, h - barH, barW - 1, barH);
        }
      } else {
        // Idle Oscilloscope Line
        ctx.beginPath();
        ctx.strokeStyle = '#ff0077';
        ctx.lineWidth = 2;
        ctx.moveTo(0, cy);
        ctx.lineTo(w, cy);
        ctx.stroke();
      }

      requestAnimationFrame(drawScope);
    }
    drawScope();
  }

  // =========================================================================
  // EUCLIDEAN HYPERPOP SEQUENCER
  // =========================================================================
  function initSequencer() {
    var stepElements = document.querySelectorAll('.vst-seq-step');
    stepElements.forEach(function (stepEl, idx) {
      stepEl.addEventListener('click', function () {
        synth.sequencer.steps[idx] = !synth.sequencer.steps[idx];
        stepEl.classList.toggle('active', synth.sequencer.steps[idx]);
      });
    });

    var playBtn = document.getElementById('seq-play-toggle');
    if (playBtn) {
      playBtn.addEventListener('click', function () {
        synth.sequencer.isPlaying = !synth.sequencer.isPlaying;
        playBtn.classList.toggle('active', synth.sequencer.isPlaying);
        playBtn.textContent = synth.sequencer.isPlaying ? '■ STOP' : '▶ RUN';

        if (synth.sequencer.isPlaying) {
          startSequencerClock();
        } else {
          stopSequencerClock();
        }
      });
    }

    var bpmSlider = document.getElementById('slider-seq-bpm');
    var bpmVal = document.getElementById('val-seq-bpm');
    if (bpmSlider) {
      bpmSlider.addEventListener('input', function () {
        synth.sequencer.bpm = parseInt(bpmSlider.value, 10);
        if (bpmVal) bpmVal.textContent = synth.sequencer.bpm + ' BPM';
        if (synth.sequencer.isPlaying) {
          stopSequencerClock();
          startSequencerClock();
        }
      });
    }
  }

  function startSequencerClock() {
    initAudio();
    var intervalMs = (60 / synth.sequencer.bpm / 4) * 1000;
    synth.sequencer.timerId = setInterval(function () {
      var step = synth.sequencer.currentStep;
      var stepElements = document.querySelectorAll('.vst-seq-step');

      stepElements.forEach(function (el, i) {
        el.classList.toggle('current', i === step);
      });

      if (synth.sequencer.steps[step]) {
        var note = synth.sequencer.notes[step];
        triggerNoteOn(note);
        setTimeout(function () { triggerNoteOff(note); }, intervalMs * 0.8);
      }

      synth.sequencer.currentStep = (step + 1) % 16;
    }, intervalMs);
  }

  function stopSequencerClock() {
    if (synth.sequencer.timerId) {
      clearInterval(synth.sequencer.timerId);
      synth.sequencer.timerId = null;
    }
    document.querySelectorAll('.vst-seq-step').forEach(function (el) {
      el.classList.remove('current');
    });
  }

  // =========================================================================
  // WAV AUDIO RECORDER & EXPORTER
  // =========================================================================
  function initAudioRecorder() {
    var recBtn = document.getElementById('vst-record-wav-btn');
    if (!recBtn) return;

    recBtn.addEventListener('click', function () {
      initAudio();
      if (!synth.recorder.isRecording) {
        startRecording();
        recBtn.classList.add('recording');
        recBtn.textContent = '⏹ STOP & SAVE WAV';
      } else {
        stopRecording();
        recBtn.classList.remove('recording');
        recBtn.textContent = '● RECORD WAV';
      }
    });
  }

  function startRecording() {
    synth.recorder.audioChunks = [];
    var stream = synth.recorder.destNode.stream;
    try {
      synth.recorder.mediaRecorder = new MediaRecorder(stream);
      synth.recorder.mediaRecorder.ondataavailable = function (e) {
        synth.recorder.audioChunks.push(e.data);
      };
      synth.recorder.mediaRecorder.onstop = function () {
        var blob = new Blob(synth.recorder.audioChunks, { type: 'audio/wav' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'SophieX_Hyperpop_Render_' + Date.now() + '.wav';
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 200);
      };
      synth.recorder.mediaRecorder.start();
      synth.recorder.isRecording = true;
    } catch (e) {
      console.error('MediaRecorder error:', e);
    }
  }

  function stopRecording() {
    if (synth.recorder.mediaRecorder && synth.recorder.isRecording) {
      synth.recorder.mediaRecorder.stop();
      synth.recorder.isRecording = false;
    }
  }

  // =========================================================================
  // CONTROLS & PRESET MANAGER
  // =========================================================================
  function initControls() {
    var presetSelect = document.getElementById('vst-preset-select');
    if (presetSelect) {
      presetSelect.addEventListener('change', function () {
        var key = presetSelect.value;
        if (PRESETS[key]) {
          synth.params = Object.assign({}, PRESETS[key]);
          applyPresetToUI(synth.params);
          if (synth.filterNode) {
            synth.filterNode.frequency.setValueAtTime(synth.params.filterCutoff, synth.ctx.currentTime);
            synth.filterNode.Q.setValueAtTime(synth.params.filterRes, synth.ctx.currentTime);
          }
          updateDistortionCurve(synth.params.drive);
        }
      });
    }

    var oscButtons = document.querySelectorAll('.vst-toggle-btn[data-osc]');
    oscButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        synth.params.oscType = btn.getAttribute('data-osc');
        oscButtons.forEach(function (b) { b.classList.toggle('active', b === btn); });
      });
    });

    var formantButtons = document.querySelectorAll('.vst-toggle-btn[data-formant]');
    formantButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        synth.params.formant = btn.getAttribute('data-formant');
        formantButtons.forEach(function (b) { b.classList.toggle('active', b === btn); });
      });
    });

    wireSlider('slider-pitch-snap', 'val-pitch-snap', function (v) { synth.params.pitchSnap = parseFloat(v); }, '%');
    wireSlider('slider-metallic-fm', 'val-metallic-fm', function (v) { synth.params.metallicFM = parseFloat(v); }, '%');
    wireSlider('slider-cutoff', 'val-cutoff', function (v) {
      synth.params.filterCutoff = parseFloat(v);
      if (synth.filterNode) synth.filterNode.frequency.setValueAtTime(synth.params.filterCutoff, synth.ctx.currentTime);
    }, ' Hz');
    wireSlider('slider-res', 'val-res', function (v) {
      synth.params.filterRes = parseFloat(v);
      if (synth.filterNode) synth.filterNode.Q.setValueAtTime(synth.params.filterRes, synth.ctx.currentTime);
    }, ' Q');
    wireSlider('slider-drive', 'val-drive', function (v) {
      synth.params.drive = parseFloat(v);
      updateDistortionCurve(synth.params.drive);
    }, '%');
  }

  function wireSlider(id, valId, callback, suffix) {
    var slider = document.getElementById(id);
    var valEl = document.getElementById(valId);
    if (!slider) return;
    slider.addEventListener('input', function () {
      var v = slider.value;
      if (valEl) valEl.textContent = v + suffix;
      callback(v);
    });
  }

  function applyPresetToUI(p) {
    setSlider('slider-pitch-snap', 'val-pitch-snap', Math.floor(p.pitchSnap * 100), '%');
    setSlider('slider-metallic-fm', 'val-metallic-fm', Math.floor(p.metallicFM * 100), '%');
    setSlider('slider-cutoff', 'val-cutoff', p.filterCutoff, ' Hz');
    setSlider('slider-res', 'val-res', p.filterRes, ' Q');
    setSlider('slider-drive', 'val-drive', Math.floor(p.drive * 100), '%');

    document.querySelectorAll('.vst-toggle-btn[data-osc]').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-osc') === p.oscType);
    });
    document.querySelectorAll('.vst-toggle-btn[data-formant]').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-formant') === p.formant);
    });
  }

  function setSlider(id, valId, val, suffix) {
    var s = document.getElementById(id);
    var v = document.getElementById(valId);
    if (s) s.value = val;
    if (v) v.textContent = val + suffix;
  }

  // =========================================================================
  // KEYBOARD BINDINGS
  // =========================================================================
  function initKeyboard() {
    var keys = document.querySelectorAll('.vst-white-key, .vst-black-key');
    keys.forEach(function (keyEl) {
      var note = keyEl.getAttribute('data-note');
      keyEl.addEventListener('mousedown', function () { triggerNoteOn(note); });
      keyEl.addEventListener('mouseup', function () { triggerNoteOff(note); });
      keyEl.addEventListener('mouseleave', function () { triggerNoteOff(note); });

      keyEl.addEventListener('touchstart', function (e) {
        e.preventDefault();
        triggerNoteOn(note);
      });
      keyEl.addEventListener('touchend', function (e) {
        e.preventDefault();
        triggerNoteOff(note);
      });
    });

    var activeKeys = {};
    window.addEventListener('keydown', function (e) {
      var k = e.key.toLowerCase();
      if (KEY_NOTE_MAP[k] && !activeKeys[k]) {
        activeKeys[k] = true;
        triggerNoteOn(KEY_NOTE_MAP[k]);
      }
      if (e.code === 'Space') {
        e.preventDefault();
        var pBtn = document.getElementById('seq-play-toggle');
        if (pBtn) pBtn.click();
      }
    });

    window.addEventListener('keyup', function (e) {
      var k = e.key.toLowerCase();
      if (KEY_NOTE_MAP[k]) {
        activeKeys[k] = false;
        triggerNoteOff(KEY_NOTE_MAP[k]);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initOscilloscope();
    initSequencer();
    initAudioRecorder();
    initControls();
    initKeyboard();
  });

})(window, document);
