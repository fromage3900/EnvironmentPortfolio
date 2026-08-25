import op, math, json, socket

def setup_harmonic_audio_streamer():
    base = op('/project1')
    if not base:
        print("Root /project1 not found")
        return
        
    net = base.op('audio_harmonic')
    if not net:
        net = base.create(baseCOMP, 'audio_harmonic')
        
    for child in list(net.children):
        child.destroy()
        
    # Create Audio Source
    audio_in = net.create(audiofileinCHOP, 'audio_in')
    audio_in.nodeX = 0
    audio_in.nodeY = 0
    
    # Filter 4 frequency bands
    # 1. Sub-Bass (20-100Hz)
    bass_filter = net.create(bandpassCHOP, 'bass_filter')
    bass_filter.par.cutoff = 60
    bass_filter.par.width = 0.8
    bass_filter.inputConnectors[0].connect(audio_in.outputConnectors[0])
    bass_filter.nodeX = 200
    bass_filter.nodeY = 150
    
    bass_analyze = net.create(analyzeCHOP, 'bass_analyze')
    bass_analyze.par.function = 4  # RMS
    bass_analyze.inputConnectors[0].connect(bass_filter.outputConnectors[0])
    bass_analyze.nodeX = 400
    bass_analyze.nodeY = 150
    
    # 2. Mid-Range (250-2500Hz)
    mid_filter = net.create(bandpassCHOP, 'mid_filter')
    mid_filter.par.cutoff = 1000
    mid_filter.par.width = 1.5
    mid_filter.inputConnectors[0].connect(audio_in.outputConnectors[0])
    mid_filter.nodeX = 200
    mid_filter.nodeY = 50
    
    mid_analyze = net.create(analyzeCHOP, 'mid_analyze')
    mid_analyze.par.function = 4 # RMS
    mid_analyze.inputConnectors[0].connect(mid_filter.outputConnectors[0])
    mid_analyze.nodeX = 400
    mid_analyze.nodeY = 50
    
    # 3. High-Frequency (4kHz-12kHz)
    high_filter = net.create(bandpassCHOP, 'high_filter')
    high_filter.par.cutoff = 8000
    high_filter.par.width = 1.2
    high_filter.inputConnectors[0].connect(audio_in.outputConnectors[0])
    high_filter.nodeX = 200
    high_filter.nodeY = -50
    
    high_analyze = net.create(analyzeCHOP, 'high_analyze')
    high_analyze.par.function = 4 # RMS
    high_analyze.inputConnectors[0].connect(high_filter.outputConnectors[0])
    high_analyze.nodeX = 400
    high_analyze.nodeY = -50
    
    # Merge CHOP
    merge = net.create(mergeCHOP, 'audio_bands')
    merge.inputConnectors[0].connect(bass_analyze.outputConnectors[0])
    merge.inputConnectors[1].connect(mid_analyze.outputConnectors[0])
    merge.inputConnectors[2].connect(high_analyze.outputConnectors[0])
    merge.nodeX = 600
    merge.nodeY = 50
    
    print("Harmonic Audio Streamer Network successfully constructed in TouchDesigner!")

setup_harmonic_audio_streamer()
