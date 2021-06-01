
class TreeWalker:

    def __init__(self):
        self.current_AST_start_line_number = None  # PROTECTS FROM MULTI-LINE STATEMENTS
        self.current_AST_end_line_number = None  # PROTECTS FROM MULTI-LINE STATEMENTS


    def generic_recurse_and_apply_function(self, token, function_to_apply):
        ''' GENERIC RECURSION PATTERN - LEFT RIGHT TOKEN
            input:  token  CPPCHECK token to recurse upon
            function_to_apply:  the function to apply to the token 
                after recursing.
            returns: None   Side effect determined by function_to_apply
            '''
        if not token:
            return

        # INITIALIZE
        left_token = right_token = None

        # LEFT
        if token.astOperand1:
            left_token = token.astOperand1
            self.generic_recurse_and_apply_function(left_token,
                                                    function_to_apply)
        # RIGHT
        if token.astOperand2:
            right_token = token.astOperand2
            self.generic_recurse_and_apply_function(right_token,
                                                    function_to_apply)

        function_to_apply(token, left_token, right_token)


    def find_min_max_line_numbers(self, token, left_token, right_token):
        ''' FIND THE MIN AND MAX LINE NUMBERS FOR THIS AST,
                PROTECT FROM MULTI-LINE STATEMENTS
            input:  token AN AST TOKEN
                    left_token  (ignored)
                    right_token  (ignored)
            returns: None  (side effect: modifies class min and max
                line number range
            '''
        if not self.current_AST_start_line_number or \
                token.linenr < self.current_AST_start_line_number:
            self.current_AST_start_line_number = token.linenr
        if not self.current_AST_end_line_number or \
                token.linenr > self.current_AST_end_line_number:
            self.current_AST_end_line_number = token.linenr


    def reset_min_max_line_numbers(self):
        ''' INITIALIZES THE AST LINE NUMBERS BACK TO NONE.
                SHOULD BE CALLED BEFORE EVERY AST IS EVALUATED
            input: None
            output: None.  side effect is setting class variables
                for min max to None
            '''
        self.current_AST_start_line_number = None
        self.current_AST_end_line_number = None


    def get_variable_tokens_and_name(self, token):
        while token.astParent and token.astParent.str in ['.']:
            token = token.astParent
        return (self.get_variable_tokens(token), self.get_variable_name(token))


    def get_variable_tokens(self, token):
        variable_tokens = []

        # LEFT RECURSE
        if token.astOperand1:
            variable_tokens.extend(self.get_variable_tokens(token.astOperand1))
        
        # SELF
        if token.variable:
            variable_tokens.append(token)

        # RIGHT_RECURSE
        if token.astOperand2:
            variable_tokens.extend(self.get_variable_tokens(token.astOperand2))

        return variable_tokens


    def get_variable_name(self, token):
        name = ''

         # LEFT RECURSE
        if token.astOperand1:
            name +=  self.get_variable_name(token.astOperand1)

        # SELF
        name += token.str

        # RIGHT RECURSE
        if token.astOperand2:
            name +=  self.get_variable_name(token.astOperand2)
 
        if token.str == '[':
            name += ']'

        return name



