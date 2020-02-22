class BinOp:
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right

	def __str__(self):
		return "{} {} {}".format(str(self.left), self.op, str(self.right))

class Parser:
	AND = 0
	OR = 1

	def __init__(self, req, precedence):
		self.req = req
		self.curr = 0
		self.sym = self.req[self.curr]
		# Details what binds tighters
		self.precedence = precedence

	def nxt(self):
		if self.curr < len(self.req):
			self.sym, self.curr = self.req[self.curr], self.curr + 1
		else:
			self.sym = None

	def factor(self):
		node = self.term()

		while self.sym == OR:
			token = self.sym
			self.nxt()
			if self.precedence == AND:
				node = BinOp(node, token, self.term())
			else:
				node = BinOp(node, token, self.expr())

		return node

	def term(self):
		node = self.expr()

		while self.sym == AND:
			token = self.sym
			self.nxt()
			if self.precedence == AND:
				node = BinOp(node, token, self.expr())
			else:
				node = BinOp(node, token, self.factor())

		return node

	def expr(self):
		res = self.sym
		self.nxt()
		return res

	def parse(self):
		self.nxt()

		if self.precedence == AND:
			return self.factor()
		else:
			return self.term()


# class Interpreter:
# 	AND = 0
# 	OR = 1
# 	def __init__(self):
# 		pass

# 	def calculate(self, parser, course_list):
# 		# base case
# 		if not isinstance(parser, BinOp):

# 			units, check_list = parser
# 			req_units = units
# 			# convert check_list to set for const lookup
# 			check_list = set(check_list)

# 			for course in course_list:
# 				if course in check_list:
# 					units -= 1
# 					# course_list is still a list to maintain ordering
# 					course_list.remove(course)
# 					if units == 0:
# 						break

# 			if units == 0:
# 				return req_units, req_units, course_list
# 			else:
# 				return req_units - units, req_units, course_list 

# 		if parser.op == AND:
# 			left_completed_courses, left_required_coures, left_course_list = self.calculate(parser.left, course_list)
# 			# Since we have an AND, we use the updated course_list from the left
# 			right_completed_courses, right_required_courses, right_course_list = self.calculate(parser.right, left_course_list)

# 			return (left_completed_courses + right_completed_courses), (left_required_coures + right_required_courses), right_course_list
# 		else:
# 			# OR case
# 			# Keep a copy to prevent aliasing
# 			course_list_copy = course_list.copy()
# 			left_completed_courses, left_required_coures, left_course_list = self.calculate(parser.left, course_list)
# 			# Since we have an AND, we use the updated course_list from the left
# 			right_completed_courses, right_required_courses, right_course_list = self.calculate(parser.right, course_list_copy)

# 			# if left side of equation is True, we propogate that up
# 			if left_completed_courses == left_required_coures or ((left_required_coures - left_completed_courses) > (right_required_courses - right_completed_courses)):
# 				return left_completed_courses, left_required_coures, left_course_list
# 			else:
# 				return right_completed_courses, right_required_courses, right_course_list




# AND = 0
# OR = 1

# course_list = ["apple", "a", "fruit", "e", "b"]

# left = (1, ["apple"])
# right = (1, ["bananna"])
# eq = (1, ["a"])

# i = Interpreter()
# print(i.calculate(eq, course_list))

# # p = Parser(["A", AND, "B", OR, "C"], AND)

# # res = p.parse()
# # print(res.right)