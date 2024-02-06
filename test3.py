def remove_subsentences(sentences):
    # 存储最终结果的列表
    filtered_sentences = []
    # 从第一行开始，依次检查是否为子句
    i = 0
    while i < len(sentences):
        # 假设当前句子不是子句
        is_subsentence = False
        # 检查后面的句子，看当前句子是否为某个句子的子句
        for j in range(i + 1, len(sentences)):
            # 如果当前句子是后面某个句子的子句，跳过当前句子
            if sentences[i] in sentences[j]:
                is_subsentence = True
                break
        # 如果当前句子不是任何句子的子句，加入结果列表
        if not is_subsentence:
            filtered_sentences.append(sentences[i])
        # 移动到下一个句子
        i += 1

    return filtered_sentences

# 示例句子列表（按行号顺序）
sentences = [
    "ABC",
    "CCBAC",
    "CCBACFG",
    "ABCD",  # 第7行
    "AB",    # 第8行
    "ABCDEF" # 第9行
    # ... 可以添加更多句子
]

# 移除子句
filtered_sentences = remove_subsentences(sentences)

# 打印结果
for sentence in filtered_sentences:
    print(sentence)