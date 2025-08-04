# from llama_index.core.tools import FunctionTool
# from tools.activity_recommendation import ActivityRecommendation
# from tools.retrieve_user_context import RetrieveUserContext
# from tools.update_session_context import UpdateSessionContext
# from tools.update_user_embeddings import UpdateUserEmbeddings
# from tools.update_user_preference import UpdateUserPreference

# def get_tools(**kwargs):
#     return [FunctionTool.from_defaults(ActivityRecommendation.recommend_activities), 
#              FunctionTool.from_defaults(RetrieveUserContext.retrieve_user_context),
#              FunctionTool.from_defaults(UpdateSessionContext.update_session_context),
#              FunctionTool.from_defaults(UpdateUserPreference.update_user_preferences),
#              FunctionTool.from_defaults(UpdateUserEmbeddings.update_user_embeddings)]