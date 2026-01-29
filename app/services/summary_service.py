# import torch # [FIX] 누락된 임포트 추가
# from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

# model_name = "digit82/ko-bart-summary"

# class SummaryService:
#     _instance = None
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
#             cls.model = BartForConditionalGeneration.from_pretrained(model_name)
#         return cls._instance

#     def generate_summary(self, text: str) -> str:
#         if not text or len(text) < 10:
#             return "내용이 너무 짧아 요약할 수 없습니다."
#         raw_input_ids = self.tokenizer.encode(text)
#         input_ids = [self.tokenizer.bos_token_id] + raw_input_ids + [self.tokenizer.eos_token_id]
#         summary_ids = self.model.generate(
#             torch.tensor([input_ids]), #
#             max_length=128,
#             num_beams=4,
#             eos_token_id=self.tokenizer.eos_token_id
#         )
#         return self.tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

#     def generate_title(self, summary: str) -> str:
#         """요약문의 앞부분을 활용해 일기 제목 생성"""
#         clean_summary = summary.replace("요약:", "").strip()
#         return f"{clean_summary[:15]}..." if len(clean_summary) > 15 else clean_summary

# summary_service = SummaryService()
