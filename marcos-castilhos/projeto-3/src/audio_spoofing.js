// Itera sobre a entrada e acessa o buffer binário
for (let item of $input.all()) {
  if (item.binary && item.binary.data) {
    // Sobrescreve os metadados
    item.binary.data.fileName = 'audio.ogg';
    item.binary.data.mimeType = 'audio/ogg';
  }
}
return $input.all();