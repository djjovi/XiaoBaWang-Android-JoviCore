@Composable
fun ChatScreen(loadSuccess: Boolean) {
    [cite_start]var messages by remember { mutableStateOf(listOf<ChatMsg>()) } 
    var inputText by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    Column {
        LazyColumn(Modifier.weight(1f)) {
            items(messages) { msg ->
                [cite_start]ChatBubble(msg.text, msg.isUser) [cite: 50]
            }
        }
        Row(Modifier.padding(16.dp)) {
            [cite_start]TextField(value = inputText, onValueChange = { inputText = it }) 
            Button(onClick = {
                val userMsg = ChatMsg(inputText, true)
                [cite_start]messages = messages + userMsg 
                scope.launch(Dispatchers.IO) {
                    [cite_start]val response = LlamaBridge.generate(userMsg.text) 
                    withContext(Dispatchers.Main) {
                        [cite_start]messages = messages + ChatMsg(response, false) 
                    }
                }
            }) { Text("发送") }
        }
    }
}
