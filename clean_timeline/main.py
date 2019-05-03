def process_tweet(tweet):
    #strip usernames
	    tweet =
		re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)','',tweet)
		    #strip newlines and unicode characters that aren't formatted
			    tweet = re.sub(r'\n|&gt;|RT :','',tweet)
				    #strip twitter urls from tweets
					    tweet =
						re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))https://t.co/([A-Za-z0-9-_,\']+)','',tweet)
						    #Remove emojis
							    RE_EMOJI =
								re.compile('[\U00010000-\U0010ffff]',
								flags=re.UNICODE)
								    tweet = RE_EMOJI.sub(r'', tweet)
									    return tweet.strip()

										def
										clean_timeline(TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET):
										    # Create Twitter Connection
											    twitter_auth =
												tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),config('TWITTER_CONSUMER_SECRET'))
												    access_token =
													TWITTER_ACCESS_TOKEN
													    access_token_secret =
														TWITTER_ACCESS_TOKEN_SECRET
														    twitter_auth.set_access_token(access_token,
															access_token_secret)
															    global TWITTER
																    TWITTER =
																	tweepy.API(twitter_auth)
																	    
																		    try:
																			        home_timeline
																					=
																					TWITTER.home_timeline(count=200,
																					                                         tweet_mode='extended',
																															                                          exlude_rts=False)
																																									          timeline
																																											  =
																																											  [{"tweet": 
																																											                       {"user_id":
																																																   u.user.id,
																																																                         "user_name"
																																																						 :
																																																						 u.user.name,
																																																						                       "tweet":
																																																											   process_tweet(u.full_text),
																																																											                         "tweet_id"
																																																																	 :
																																																																	 u.id_str
																																																																	 }
																																																																	                     }
																																																																						                    for
																																																																											u
																																																																											in
																																																																											home_timeline]
																																																																											        return
																																																																													json.dumps(timeline)

																																																																													    except
																																																																														tweepy.TweepError:
																																																																														        print("tweepy.TweepError")
																																																																																        
																																																																																		    except:
																																																																																			        e
																																																																																					=
																																																																																					sys.exc_info()[0]
																																																																																					        print("Error:
																																																																																							%s"
																																																																																							%%
																																																																																							%e)
																																																																																							        
																																																																																									        
																																																																																											def
																																																																																											process_request(request):
																																																																																											    """
																																																																																												Responds
																																																																																												to
																																																																																												a
																																																																																												GET
																																																																																												request
																																																																																												with
																																																																																												"Hello
																																																																																												world!".
																																																																																												Forbids
																																																																																												a
																																																																																												PUT
																																																																																												request.
																																																																																												    Args:
																																																																																													        request
																																																																																															(flask.Request):
																																																																																															The
																																																																																															request
																																																																																															object.
																																																																																															        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
																																																																																																	    Returns:
																																																																																																		        The
																																																																																																				response
																																																																																																				text,
																																																																																																				or
																																																																																																				any
																																																																																																				set
																																																																																																				of
																																																																																																				values
																																																																																																				that
																																																																																																				can
																																																																																																				be
																																																																																																				turned
																																																																																																				into
																																																																																																				a
																																																																																																				         Response
																																																																																																						 object
																																																																																																						 using
																																																																																																						 `make_response`
																																																																																																						         <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
																																																																																																								     """
																																																																																																									     from
																																																																																																										 flask
																																																																																																										 import
																																																																																																										 abort

																																																																																																										     content_type
																																																																																																											 =
																																																																																																											 request.headers['content-type']
																																																																																																											     request_json
																																																																																																												 =
																																																																																																												 request.get_json(silent=True)
																																																																																																												     request_args
																																																																																																													 =
																																																																																																													 request.args

																																																																																																													     if
																																																																																																														 content_type
																																																																																																														 ==
																																																																																																														 'application/json': 
																																																																																																														         request_json
																																																																																																																 =
																																																																																																																 request.get_json(silent=True)
																																																																																																																         # TWITTER_ACCESS_TOKEN
																																																																																																																		 # check/set/error
																																																																																																																		         if
																																																																																																																				 request_json
																																																																																																																				 and
																																																																																																																				 'TWITTER_ACCESS_TOKEN'
																																																																																																																				 in
																																																																																																																				 request_json:
																																																																																																																				             TWITTER_ACCESS_TOKEN
																																																																																																																							 =
																																																																																																																							 request_json['TWITTER_ACCESS_TOKEN']
																																																																																																																							         else:
																																																																																																																									             raise
																																																																																																																												 ValueError("Missing
																																																																																																																												 a
																																																																																																																												 'TWITTER_ACCESS_TOKEN'")
																																																																																																																												         # TWITTER_ACCESS_TOKEN_SECRET
																																																																																																																														 # check/set/error
																																																																																																																														         if
																																																																																																																																 request_json
																																																																																																																																 and
																																																																																																																																 'TWITTER_ACCESS_TOKEN_SECRET'
																																																																																																																																 in
																																																																																																																																 request_json:
																																																																																																																																             TWITTER_ACCESS_TOKEN_SECRET
																																																																																																																																			 =
																																																																																																																																			 request_json['TWITTER_ACCESS_TOKEN_SECRET']
																																																																																																																																			         else:
																																																																																																																																					             raise
																																																																																																																																								 ValueError("Missing
																																																																																																																																								 a
																																																																																																																																								 'TWITTER_ACCESS_TOKEN_SECRET'")
																																																																																																																																								         
																																																																																																																																										         # Call
																																																																																																																																												 # the
																																																																																																																																												 # function
																																																																																																																																												 # for
																																																																																																																																												 # the
																																																																																																																																												 # POST
																																																																																																																																												 # request. 
																																																																																																																																												         if
																																																																																																																																														 request.method
																																																																																																																																														 ==
																																																																																																																																														 'POST':
																																																																																																																																														             return
																																																																																																																																																	 clean_timeline(TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
																																																																																																																																																	     else:
																																																																																																																																																		         return
																																																																																																																																																				 abort(405)
