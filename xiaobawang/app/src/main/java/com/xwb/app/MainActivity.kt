class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val decryptedFile = File(filesDir, "xbw-q4km.gguf")
        if (!decryptedFile.exists()) {
            AESUtil.decrypt(assets.open("xbw-q4km.gguf.enc"), 
                           [cite_start]decryptedFile.outputStream(), "你的密钥") 
        }
        [cite_start]val success = LlamaBridge.loadModel(decryptedFile.absolutePath) 
        [cite_start]setContent { ChatScreen(success) } 
    }
}
