%module model
%{
#include "model/metamodel/object.h"
%}

%include "util/attributedclass.h"

namespace FIFE { namespace model {

	class Object : public AttributedClass {
		public:

			~Object();

			
			

		private:

			Object(const Object* inherited);
	};
}}
