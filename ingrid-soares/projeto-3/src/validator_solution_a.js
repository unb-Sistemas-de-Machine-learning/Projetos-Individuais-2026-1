/**
 * Validator Node: Solution A
 * Valida se a resposta do LLM está em um formato JSON esperado
 */

const output = items[0].json;

// Valida se o objeto contém os campos necessários
if (!output.fase_reconhecimento || !output.fase_validacao || !output.relatorio_riscos) {
    throw new Error("Formato inválido: JSON não contém todas as fases esperadas.");
}

// Retorna os dados para o próximo nó se validado
return {
    json: {
        status: "success",
        data: output
    }
};
