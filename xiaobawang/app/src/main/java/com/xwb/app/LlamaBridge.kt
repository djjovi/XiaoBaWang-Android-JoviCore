package com.xbw.app

object LlamaBridge {
    init {
        [cite_start]System.loadLibrary("llama") // 加载编译出的SO库 [cite: 9]
    }
    [cite_start]external fun loadModel(path: String): Boolean [cite: 21]
    [cite_start]external fun generate(prompt: String): String [cite: 21]
    [cite_start]external fun releaseModel() [cite: 21]
}
